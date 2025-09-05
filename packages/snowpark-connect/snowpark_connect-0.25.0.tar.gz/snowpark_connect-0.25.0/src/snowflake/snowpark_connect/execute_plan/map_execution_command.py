#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
import re
import uuid
from collections import Counter

import pyspark.sql.connect.proto.base_pb2 as proto_base
import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake.snowpark import DataFrame, Session
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark_connect.column_name_handler import ColumnNames
from snowflake.snowpark_connect.config import global_config, sessions_config
from snowflake.snowpark_connect.constants import SERVER_SIDE_SESSION_ID
from snowflake.snowpark_connect.execute_plan.utils import pandas_to_arrow_batches_bytes
from snowflake.snowpark_connect.expression import map_udf
from snowflake.snowpark_connect.relation import map_udtf
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.relation.map_sql import map_sql_to_pandas_df
from snowflake.snowpark_connect.relation.write.map_write import map_write, map_write_v2
from snowflake.snowpark_connect.utils.context import get_session_id
from snowflake.snowpark_connect.utils.identifiers import (
    spark_to_sf_single_id,
    spark_to_sf_single_id_with_unquoting,
)
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

_INTERNAL_VIEW_PREFIX = "__SC_RENAMED_V_"

_CREATE_VIEW_PATTERN = re.compile(r"create\s+or\s+replace\s+view", re.IGNORECASE)


def _create_column_rename_map(
    columns: list[ColumnNames], rename_duplicated: bool
) -> dict:
    if rename_duplicated is False:
        # if we are not renaming duplicated columns, we can just return the original names
        return {
            col.snowpark_name: spark_to_sf_single_id(col.spark_name, is_column=True)
            for col in columns
        }

    column_counts = Counter()
    not_renamed_cols = []
    renamed_cols = []

    for col in columns:
        new_column_name = col.spark_name
        normalized_name = new_column_name.lower()
        column_counts[normalized_name] += 1

        if column_counts[normalized_name] > 1:
            new_column_name = (
                f"{new_column_name}_DEDUP_{column_counts[normalized_name] - 1}"
            )
            renamed_cols.append(ColumnNames(new_column_name, col.snowpark_name, []))
        else:
            not_renamed_cols.append(ColumnNames(new_column_name, col.snowpark_name, []))

    if len(renamed_cols) == 0:
        return {
            col.snowpark_name: spark_to_sf_single_id(col.spark_name, is_column=True)
            for col in not_renamed_cols
        }

    # we need to make sure that we don't have duplicated names after renaming
    # columns that were not renamed in this iteration should have priority over renamed duplicates
    return _create_column_rename_map(not_renamed_cols + renamed_cols, True)


def _find_duplicated_columns(
    columns: list[ColumnNames],
) -> (list[str], list[ColumnNames]):
    duplicates = []
    remaining_columns = []
    seen = set()
    for col in columns:
        if col.spark_name in seen:
            duplicates.append(col.snowpark_name)
        else:
            seen.add(col.spark_name)
            remaining_columns.append(col)
    return duplicates, remaining_columns


def map_execution_command(
    request: proto_base.ExecutePlanRequest,
) -> proto_base.ExecutePlanResponse | None:
    logger.info(request.plan.command.WhichOneof("command_type").upper())
    match request.plan.command.WhichOneof("command_type"):
        case "create_dataframe_view":
            req = request.plan.command.create_dataframe_view
            input_df_container = map_relation(req.input)
            input_df = input_df_container.dataframe
            column_map = input_df_container.column_map

            session_config = sessions_config[get_session_id()]
            duplicate_column_names_handling_mode = session_config[
                "snowpark.connect.views.duplicate_column_names_handling_mode"
            ]

            # rename columns to match spark names
            if duplicate_column_names_handling_mode == "rename":
                # deduplicate column names by appending _DEDUP_1, _DEDUP_2, etc.
                input_df = input_df.rename(
                    _create_column_rename_map(column_map.columns, True)
                )
            elif duplicate_column_names_handling_mode == "drop":
                # Drop duplicate column names by removing all but the first occurrence.
                duplicated_columns, remaining_columns = _find_duplicated_columns(
                    column_map.columns
                )
                if len(duplicated_columns) > 0:
                    input_df = input_df.drop(*duplicated_columns)
                input_df = input_df.rename(
                    _create_column_rename_map(remaining_columns, False)
                )
            else:
                # rename columns without deduplication
                input_df = input_df.rename(
                    _create_column_rename_map(column_map.columns, False)
                )

            if req.is_global:
                view_name = [global_config.spark_sql_globalTempDatabase, req.name]
            else:
                view_name = [req.name]
            view_name = [
                spark_to_sf_single_id_with_unquoting(part) for part in view_name
            ]

            if req.replace:
                try:
                    input_df.create_or_replace_temp_view(view_name)
                except SnowparkSQLException as exc:
                    if _is_error_caused_by_view_referencing_itself(exc):
                        # This error is caused by statement with self reference like `CREATE VIEW A AS SELECT X FROM A`.
                        _create_chained_view(input_df, view_name)
                    else:
                        raise
            else:
                input_df.create_temp_view(view_name)
        case "write_stream_operation_start":
            match request.plan.command.write_stream_operation_start.format:
                case "console":
                    # TODO: Make the console output work with Spark style formatting.
                    # result_df: pandas.DataFrame = map_relation(
                    #     relation_proto.Relation(
                    #         show_string=relation_proto.ShowString(
                    #             input=request.plan.command.write_stream_operation_start.input,
                    #             num_rows=100,
                    #             truncate=False,
                    #         )
                    #     )
                    # )
                    # logger.info(result_df.iloc[0, 0])
                    map_relation(
                        request.plan.command.write_stream_operation_start.input
                    ).show()
        case "sql_command":
            sql_command = request.plan.command.sql_command
            pandas_df, schema = map_sql_to_pandas_df(
                sql_command.sql, sql_command.args, sql_command.pos_args
            )
            # SELECT query in SQL command will return None instead of Pandas DF to enable lazy evaluation
            if pandas_df is not None:
                relation = relation_proto.Relation(
                    local_relation=relation_proto.LocalRelation(
                        data=pandas_to_arrow_batches_bytes(pandas_df),
                        schema=schema,
                    )
                )
            else:
                # Return the original SQL query.
                # This is what native Spark Connect does, and the Scala client expects it.
                relation = relation_proto.Relation(
                    sql=relation_proto.SQL(
                        query=sql_command.sql,
                        args=sql_command.args,
                        pos_args=sql_command.pos_args,
                    )
                )
            return proto_base.ExecutePlanResponse(
                session_id=request.session_id,
                operation_id=SERVER_SIDE_SESSION_ID,
                sql_command_result=proto_base.ExecutePlanResponse.SqlCommandResult(
                    relation=relation
                ),
            )
        case "write_operation":
            map_write(request)

        case "write_operation_v2":
            map_write_v2(request)

        case "register_function":
            map_udf.register_udf(request.plan.command.register_function)

        case "register_table_function":
            map_udtf.register_udtf(request.plan.command.register_table_function)

        case other:
            raise SnowparkConnectNotImplementedError(
                f"Command type {other} not implemented"
            )


def _generate_random_builtin_view_name() -> str:
    return _INTERNAL_VIEW_PREFIX + str(uuid.uuid4()).replace("-", "")


def _is_error_caused_by_view_referencing_itself(exc: Exception) -> bool:
    return "view definition refers to view being defined" in str(exc).lower()


def _create_chained_view(input_df: DataFrame, view_name: str) -> None:
    """
    In order to create a view, which references itself, Spark would here take the previous
    definition of A and paste it in place of `FROM A`. Snowflake would fail in such case, so
    as a workaround, we create a chain of internal views instead. This function:
    1. Renames previous definition of A to some internal name (instead of deleting).
    2. Adjusts the DDL of a new statement to reference the name of a renmaed internal view, instead of itself.
    """

    session = Session.get_active_session()

    view_name = ".".join(view_name)

    tmp_name = _generate_random_builtin_view_name()
    old_name_replacement = _generate_random_builtin_view_name()

    input_df.create_or_replace_temp_view(tmp_name)

    session.sql(f"ALTER VIEW {view_name} RENAME TO {old_name_replacement}").collect()

    ddl: str = session.sql(f"SELECT GET_DDL('VIEW', '{tmp_name}')").collect()[0][0]

    ddl = ddl.replace(view_name, old_name_replacement)

    # GET_DDL result doesn't contain `TEMPORARY`, it's likely a bug.
    ddl = _CREATE_VIEW_PATTERN.sub("create or replace temp view", ddl)

    session.sql(ddl).collect()

    session.sql(f"ALTER VIEW {tmp_name} RENAME TO {view_name}").collect()
