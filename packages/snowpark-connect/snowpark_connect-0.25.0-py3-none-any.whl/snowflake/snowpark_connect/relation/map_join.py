#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
from collections import Counter
from functools import reduce

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.errors.exceptions.base import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark_connect.column_name_handler import JoinColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.constants import COLUMN_METADATA_COLLISION_KEY
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.error.error_utils import SparkException
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import JoinExpressionTyper
from snowflake.snowpark_connect.hidden_column import HiddenColumn
from snowflake.snowpark_connect.relation.map_relation import (
    NATURAL_JOIN_TYPE_BASE,
    map_relation,
)
from snowflake.snowpark_connect.utils.context import (
    push_evaluating_join_condition,
    push_sql_scope,
    set_sql_plan_name,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

USING_COLUMN_NOT_FOUND_ERROR = "[UNRESOLVED_USING_COLUMN_FOR_JOIN] USING column `{0}` not found on the {1} side of the join. The {1}-side columns: {2}"

DUPLICATED_JOIN_COL_LSUFFIX = "_left"
DUPLICATED_JOIN_COL_RSUFFIX = "_right"


def map_join(rel: relation_proto.Relation) -> DataFrameContainer:
    left_container: DataFrameContainer = map_relation(rel.join.left)
    right_container: DataFrameContainer = map_relation(rel.join.right)

    left_input: snowpark.DataFrame = left_container.dataframe
    right_input: snowpark.DataFrame = right_container.dataframe
    is_natural_join = rel.join.join_type >= NATURAL_JOIN_TYPE_BASE
    using_columns = rel.join.using_columns
    if is_natural_join:
        rel.join.join_type -= NATURAL_JOIN_TYPE_BASE
        left_spark_columns = left_container.column_map.get_spark_columns()
        right_spark_columns = right_container.column_map.get_spark_columns()
        common_spark_columns = [
            x for x in left_spark_columns if x in right_spark_columns
        ]
        using_columns = common_spark_columns

    match rel.join.join_type:
        case relation_proto.Join.JOIN_TYPE_UNSPECIFIED:
            # TODO: Understand what UNSPECIFIED Join type is
            raise SnowparkConnectNotImplementedError("Unspecified Join Type")
        case relation_proto.Join.JOIN_TYPE_INNER:
            join_type = "inner"
        case relation_proto.Join.JOIN_TYPE_FULL_OUTER:
            join_type = "full_outer"
        case relation_proto.Join.JOIN_TYPE_LEFT_OUTER:
            join_type = "left"
        case relation_proto.Join.JOIN_TYPE_RIGHT_OUTER:
            join_type = "right"
        case relation_proto.Join.JOIN_TYPE_LEFT_ANTI:
            join_type = "leftanti"
        case relation_proto.Join.JOIN_TYPE_LEFT_SEMI:
            join_type = "leftsemi"
        case relation_proto.Join.JOIN_TYPE_CROSS:
            join_type = "cross"
        case other:
            raise SnowparkConnectNotImplementedError(f"Other Join Type: {other}")

    # This handles case sensitivity for using_columns
    case_corrected_right_columns: list[str] = []
    hidden_columns = set()
    # Propagate the hidden columns from left/right inputs to the result in case of chained joins
    if left_container.column_map.hidden_columns:
        hidden_columns.update(left_container.column_map.hidden_columns)

    if right_container.column_map.hidden_columns:
        hidden_columns.update(right_container.column_map.hidden_columns)

    if rel.join.HasField("join_condition"):
        assert not using_columns

        left_columns = list(left_container.column_map.spark_to_col.keys())
        right_columns = list(right_container.column_map.spark_to_col.keys())

        # All PySpark join types are in the format of JOIN_TYPE_XXX.
        # We remove the first 10 characters (JOIN_TYPE_) and replace all underscores with spaces to match the exception.
        pyspark_join_type = relation_proto.Join.JoinType.Name(rel.join.join_type)[
            10:
        ].replace("_", " ")
        with push_sql_scope(), push_evaluating_join_condition(
            pyspark_join_type, left_columns, right_columns
        ):
            if left_container.alias is not None:
                set_sql_plan_name(left_container.alias, rel.join.left.common.plan_id)
            if right_container.alias is not None:
                set_sql_plan_name(right_container.alias, rel.join.right.common.plan_id)
            _, join_expression = map_single_column_expression(
                rel.join.join_condition,
                column_mapping=JoinColumnNameMap(
                    left_container.column_map,
                    right_container.column_map,
                ),
                typer=JoinExpressionTyper(left_input, right_input),
            )
        result: snowpark.DataFrame = left_input.join(
            right=right_input,
            on=join_expression.col,
            how=join_type,
            lsuffix=DUPLICATED_JOIN_COL_LSUFFIX,
            rsuffix=DUPLICATED_JOIN_COL_RSUFFIX,
        )
    elif using_columns:
        if any(
            left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                c, allow_non_exists=True, return_first=True
            )
            is None
            for c in using_columns
        ):
            import pyspark

            raise pyspark.errors.AnalysisException(
                USING_COLUMN_NOT_FOUND_ERROR.format(
                    next(
                        c
                        for c in using_columns
                        if left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                            c, allow_non_exists=True, return_first=True
                        )
                        is None
                    ),
                    "left",
                    left_container.column_map.get_spark_columns(),
                )
            )
        if any(
            right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                c, allow_non_exists=True, return_first=True
            )
            is None
            for c in using_columns
        ):
            import pyspark

            raise pyspark.errors.AnalysisException(
                USING_COLUMN_NOT_FOUND_ERROR.format(
                    next(
                        c
                        for c in using_columns
                        if right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                            c, allow_non_exists=True, return_first=True
                        )
                        is None
                    ),
                    "right",
                    right_container.column_map.get_spark_columns(),
                )
            )

        using_columns_snowpark_names = (
            left_container.column_map.get_snowpark_column_names_from_spark_column_names(
                list(using_columns), return_first=True
            )
        )

        using_columns_snowpark_types = [
            left_container.dataframe.schema.fields[idx].datatype
            for idx, col in enumerate(left_container.column_map.get_snowpark_columns())
            if col in using_columns_snowpark_names
        ]

        # Round trip the using columns through the column map to get the correct names
        # in order to support case sensitivity.
        # TODO: case_corrected_left_columns / case_corrected_right_columns may no longer be required as Snowpark dataframe preserves the column casing now.
        case_corrected_left_columns = (
            left_container.column_map.get_spark_column_names_from_snowpark_column_names(
                using_columns_snowpark_names
            )
        )
        case_corrected_right_columns = right_container.column_map.get_spark_column_names_from_snowpark_column_names(
            right_container.column_map.get_snowpark_column_names_from_spark_column_names(
                list(using_columns), return_first=True
            )
        )
        using_columns = zip(case_corrected_left_columns, case_corrected_right_columns)
        # We cannot assume that Snowpark will have the same names for left and right columns,
        # so we convert ["a", "b"] into (left["a"] == right["a"] & left["b"] == right["b"]),
        # then drop right["a"] and right["b"].
        snowpark_using_columns = [
            (
                left_input[
                    left_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        lft, return_first=True
                    )
                ],
                right_input[
                    right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        r, return_first=True
                    )
                ],
            )
            for lft, r in using_columns
        ]
        joined_df = left_input.join(
            right=right_input,
            on=reduce(
                snowpark.Column.__and__,
                (left == right for left, right in snowpark_using_columns),
            ),
            how=join_type,
            rsuffix=DUPLICATED_JOIN_COL_RSUFFIX,
        )
        # If we disambiguated the snowpark_using_columns during the join, we need to update 'snowpark_using_columns' to
        # use the disambiguated names.
        disambiguated_snowpark_using_columns = []

        # Ignore disambiguation for LEFT SEMI JOIN and LEFT ANTI JOIN because they drop the right columns, so it'll never disambiguate.
        if join_type in ["leftsemi", "leftanti"]:
            disambiguated_snowpark_using_columns = snowpark_using_columns
        else:
            normalized_joined_columns = [
                unquote_if_quoted(col) for col in joined_df.columns
            ]
            # snowpark_using_columns is a list of tuples of snowpark columns, joined_df.columns is a list of strings of column names
            for (left, right) in snowpark_using_columns:
                normalized_left_name = unquote_if_quoted(left.getName())
                normalized_right_name = unquote_if_quoted(right.getName())

                # are both left and right in joined_df? if not, it's been disambiguated
                if (
                    normalized_left_name in normalized_joined_columns
                    and normalized_right_name in normalized_joined_columns
                ):
                    # we want to just add this
                    disambiguated_snowpark_using_columns.append((left, right))
                else:
                    # we need to figure out the disambiguated names and add those - it only disambiguates if left == right
                    disambiguated_left: snowpark.Column | None = None
                    disambiguated_right: snowpark.Column | None = None

                    for col in normalized_joined_columns:
                        quoted_col = f'"{col}"'
                        # get the column name and cross check it to see if it ends with the og name
                        if col.endswith(normalized_left_name) and col.startswith("l_"):
                            disambiguated_left = joined_df[quoted_col]
                        elif col.endswith(normalized_right_name) and col.startswith(
                            "r_"
                        ):
                            disambiguated_right = joined_df[quoted_col]

                        # If we have both disambiguated columns, we can break out of the loop to save processing time
                        if (
                            disambiguated_left is not None
                            and disambiguated_right is not None
                        ):
                            break
                    if disambiguated_left is None or disambiguated_right is None:
                        raise AnalysisException(
                            f"Disambiguated columns not found for {normalized_left_name} and {normalized_right_name}."
                        )
                    disambiguated_snowpark_using_columns.append(
                        (disambiguated_left, disambiguated_right)
                    )

        # For outer joins, we need to preserve join keys from both sides using COALESCE
        """
        CHANGES:
            - IF CASE
                - Need to drop the using columns
                - Need to create the hidden_columns DF with the using columns from right and left
            - ELSE CASE
                - Need to drop the right side using columns
                - Need to create the hidden_columns DF with the using columns from right
        """
        if join_type == "full_outer":
            coalesced_columns = []
            for i, (left_col, _right_col) in enumerate(snowpark_using_columns):
                # Use the original user-specified column name to preserve case sensitivity
                # Use the disambiguated columns for coalescing
                disambiguated_left_col = disambiguated_snowpark_using_columns[i][0]
                disambiguated_right_col = disambiguated_snowpark_using_columns[i][1]

                coalesced_col = snowpark_fn.coalesce(
                    disambiguated_left_col, disambiguated_right_col
                ).alias(left_col.get_name())
                coalesced_columns.append(coalesced_col)

                # Create HiddenColumn objects for each hidden column
                hidden_left = HiddenColumn(
                    hidden_snowpark_name=disambiguated_left_col.getName(),
                    spark_name=case_corrected_left_columns[i],
                    visible_snowpark_name=left_col.get_name(),
                    qualifiers=left_container.column_map.get_qualifier_for_spark_column(
                        case_corrected_left_columns[i]
                    ),
                    original_position=left_container.column_map.get_spark_columns().index(
                        case_corrected_left_columns[i]
                    ),
                )

                hidden_right = HiddenColumn(
                    hidden_snowpark_name=disambiguated_right_col.getName(),
                    spark_name=case_corrected_right_columns[i],
                    visible_snowpark_name=left_col.get_name(),
                    qualifiers=right_container.column_map.get_qualifier_for_spark_column(
                        case_corrected_right_columns[i]
                    ),
                    original_position=right_container.column_map.get_spark_columns().index(
                        case_corrected_right_columns[i]
                    ),
                )
                hidden_columns.update(
                    [
                        hidden_left,
                        hidden_right,
                    ]
                )

            # All non-hidden columns (not including the coalesced columns)
            other_columns = [
                snowpark_fn.col(col_name)
                for col_name in joined_df.columns
                if col_name not in [col.hidden_snowpark_name for col in hidden_columns]
            ]
            result = joined_df.select(coalesced_columns + other_columns)

        else:
            result = joined_df.drop(*(right for _, right in snowpark_using_columns))
            # We never run into the disambiguation case unless it's a full outer join.
            for i, (left_col, right_col) in enumerate(
                disambiguated_snowpark_using_columns
            ):
                # Only right side columns are hidden
                hidden_col = HiddenColumn(
                    hidden_snowpark_name=right_col.getName(),
                    spark_name=case_corrected_right_columns[i],
                    visible_snowpark_name=left_col.getName(),
                    qualifiers=right_container.column_map.get_qualifier_for_spark_column(
                        case_corrected_right_columns[i]
                    ),
                    original_position=right_container.column_map.get_spark_columns().index(
                        case_corrected_right_columns[i]
                    ),
                )
                hidden_columns.add(hidden_col)
    else:
        if join_type != "cross" and not global_config.spark_sql_crossJoin_enabled:
            raise SparkException.implicit_cartesian_product("inner")
        result: snowpark.DataFrame = left_input.join(
            right=right_input,
            how=join_type,
        )

    if join_type in ["leftanti", "leftsemi"]:
        # Join types that only return columns from the left side:
        # - LEFT SEMI JOIN: Returns left rows that have matches in right table (no right columns)
        # - LEFT ANTI JOIN: Returns left rows that have NO matches in right table (no right columns)
        # Both preserve only the columns from the left DataFrame without adding any columns from the right.
        spark_cols_after_join = left_container.column_map.get_spark_columns()
        snowpark_cols_after_join = left_container.column_map.get_snowpark_columns()
        snowpark_col_types = [
            f.datatype for f in left_container.dataframe.schema.fields
        ]
        qualifiers = left_container.column_map.get_qualifiers()
    elif join_type == "full_outer" and using_columns:
        # We want the coalesced columns to be first, followed by all the left and right columns (excluding using columns)
        spark_cols_after_join: list[str] = []
        snowpark_cols_after_join: list[str] = []
        snowpark_col_types: list[str] = []

        left_container_snowpark_columns = (
            left_container.column_map.get_snowpark_columns()
        )
        right_container_snowpark_columns = (
            right_container.column_map.get_snowpark_columns()
        )

        qualifiers = []
        for i in range(len(case_corrected_left_columns)):
            spark_cols_after_join.append(case_corrected_left_columns[i])
            snowpark_cols_after_join.append(using_columns_snowpark_names[i])
            snowpark_col_types.append(using_columns_snowpark_types[i])
            qualifiers.append([])

        # Handle adding left and right columns, excluding the using columns
        for i, spark_col in enumerate(left_container.column_map.get_spark_columns()):
            if (
                spark_col not in case_corrected_left_columns
                or spark_col in left_container.column_map.get_spark_columns()[:i]
            ):
                spark_cols_after_join.append(spark_col)
                snowpark_cols_after_join.append(left_container_snowpark_columns[i])
                qualifiers.append(
                    left_container.column_map.get_qualifier_for_spark_column(spark_col)
                )

                snowpark_col_types.append(
                    left_container.dataframe.schema.fields[i].datatype
                )

        for i, spark_col in enumerate(right_container.column_map.get_spark_columns()):
            if (
                spark_col not in case_corrected_right_columns
                or spark_col in right_container.column_map.get_spark_columns()[:i]
            ):
                spark_cols_after_join.append(spark_col)
                snowpark_cols_after_join.append(right_container_snowpark_columns[i])
                qualifiers.append(
                    right_container.column_map.get_qualifier_for_spark_column(spark_col)
                )

                snowpark_col_types.append(
                    right_container.dataframe.schema.fields[i].datatype
                )

    else:
        spark_cols_after_join = left_container.column_map.get_spark_columns()
        snowpark_cols_after_join = left_container.column_map.get_snowpark_columns()
        snowpark_col_types = [
            f.datatype for f in left_container.dataframe.schema.fields
        ]

        qualifiers = left_container.column_map.get_qualifiers()

        right_df_snowpark_columns = right_container.column_map.get_snowpark_columns()

        for i, spark_col in enumerate(right_container.column_map.get_spark_columns()):
            if (
                spark_col not in case_corrected_right_columns
                or spark_col in right_container.column_map.get_spark_columns()[:i]
            ):
                spark_cols_after_join.append(spark_col)
                snowpark_cols_after_join.append(right_df_snowpark_columns[i])
                snowpark_col_types.append(
                    right_container.dataframe.schema.fields[i].datatype
                )

                qualifiers.append(
                    right_container.column_map.get_qualifier_for_spark_column(spark_col)
                )

    snowpark_cols_after_join_deduplicated = []
    snowpark_cols_after_join_counter = Counter(snowpark_cols_after_join)
    seen_duplicated_columns = set()

    for col in snowpark_cols_after_join:
        if snowpark_cols_after_join_counter[col] == 2:
            # This means that the same column exists twice in the joined df, likely due to a self-join and
            # we need to lsuffix and rsuffix to the names of both columns, similar to what Snowpark did under the hood.

            suffix = (
                DUPLICATED_JOIN_COL_RSUFFIX
                if col in seen_duplicated_columns
                else DUPLICATED_JOIN_COL_LSUFFIX
            )
            unquoted_col = unquote_if_quoted(col)
            quoted = quote_name_without_upper_casing(unquoted_col + suffix)
            snowpark_cols_after_join_deduplicated.append(quoted)

            seen_duplicated_columns.add(col)
        else:
            snowpark_cols_after_join_deduplicated.append(col)

    column_metadata = {}
    if left_container.column_map.column_metadata:
        column_metadata.update(left_container.column_map.column_metadata)

    if right_container.column_map.column_metadata:
        for key, value in right_container.column_map.column_metadata.items():
            if key not in column_metadata:
                column_metadata[key] = value
            else:
                # In case of collision, use snowpark's column's expr_id as prefix.
                # this is a temporary solution until SNOW-1926440 is resolved.
                try:
                    snowpark_name = right_container.column_map.get_snowpark_column_name_from_spark_column_name(
                        key
                    )
                    expr_id = right_input[snowpark_name]._expression.expr_id
                    updated_key = COLUMN_METADATA_COLLISION_KEY.format(
                        expr_id=expr_id, key=snowpark_name
                    )
                    column_metadata[updated_key] = value
                except Exception:
                    # ignore any errors that happens while fetching the metadata
                    pass

    result_container = DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=spark_cols_after_join,
        snowpark_column_names=snowpark_cols_after_join_deduplicated,
        column_metadata=column_metadata,
        column_qualifiers=qualifiers,
        hidden_columns=hidden_columns,
        snowpark_column_types=snowpark_col_types,
    )

    if rel.join.using_columns:
        # When join 'using_columns', the 'join columns' should go first in result DF.
        idxs_to_shift = [
            spark_cols_after_join.index(left_col_name)
            for left_col_name in case_corrected_left_columns
        ]

        def reorder(lst: list) -> list:
            to_move = [lst[i] for i in idxs_to_shift]
            remaining = [el for i, el in enumerate(lst) if i not in idxs_to_shift]
            return to_move + remaining

        # Create reordered DataFrame
        reordered_df = result_container.dataframe.select(
            [snowpark_fn.col(c) for c in reorder(result_container.dataframe.columns)]
        )

        # Create new container with reordered metadata
        original_df = result_container.dataframe
        return DataFrameContainer.create_with_column_mapping(
            dataframe=reordered_df,
            spark_column_names=reorder(result_container.column_map.get_spark_columns()),
            snowpark_column_names=reorder(
                result_container.column_map.get_snowpark_columns()
            ),
            column_metadata=column_metadata,
            column_qualifiers=reorder(qualifiers),
            table_name=result_container.table_name,
            cached_schema_getter=lambda: snowpark.types.StructType(
                reorder(original_df.schema.fields)
            ),
            hidden_columns=hidden_columns,
        )

    return result_container
