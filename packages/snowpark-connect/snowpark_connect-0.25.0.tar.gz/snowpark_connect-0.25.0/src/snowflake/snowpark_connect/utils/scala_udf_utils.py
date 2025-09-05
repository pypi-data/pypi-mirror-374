#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
"""
Scala UDF utilities for Snowpark Connect.

This module provides utilities for creating and managing Scala User-Defined Functions (UDFs)
in Snowflake through Snowpark Connect. It handles the conversion between different type systems
(Snowpark, Scala, Snowflake, Spark protobuf) and generates the necessary SQL DDL statements
for UDF creation.

Key components:
- ScalaUdf: Reference class for Scala UDFs
- ScalaUDFDef: Definition class for Scala UDF creation
- Type mapping functions for different type systems
- UDF creation and management utilities
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List

import snowflake.snowpark.types as snowpark_type
import snowflake.snowpark_connect.includes.python.pyspark.sql.connect.proto.types_pb2 as types_proto
from snowflake.snowpark_connect.resources_initializer import RESOURCE_PATH
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.utils.udf_utils import (
    ProcessCommonInlineUserDefinedFunction,
)

# Prefix used for internally generated Scala UDF names to avoid conflicts
CREATE_SCALA_UDF_PREFIX = "__SC_BUILD_IN_CREATE_UDF_SCALA_"


class ScalaUdf:
    """
    Reference class for Scala UDFs, providing similar properties like Python UserDefinedFunction.

    This class serves as a lightweight reference to a Scala UDF that has been created
    in Snowflake, storing the essential metadata needed for function calls.
    """

    def __init__(
        self,
        name: str,
        input_types: List[snowpark_type.DataType],
        return_type: snowpark_type.DataType,
    ) -> None:
        """
        Initialize a Scala UDF reference.

        Args:
            name: The name of the UDF in Snowflake
            input_types: List of input parameter types
            return_type: The return type of the UDF
        """
        self.name = name
        self._input_types = input_types
        self._return_type = return_type


@dataclass(frozen=True)
class Param:
    """
    Represents a function parameter with name and data type.

    Attributes:
        name: Parameter name
        data_type: Parameter data type as a string
    """

    name: str
    data_type: str


@dataclass(frozen=True)
class NullHandling(str, Enum):
    """
    Enumeration for UDF null handling behavior.

    Determines how the UDF behaves when input parameters contain null values.
    """

    RETURNS_NULL_ON_NULL_INPUT = "RETURNS NULL ON NULL INPUT"
    CALLED_ON_NULL_INPUT = "CALLED ON NULL INPUT"


@dataclass(frozen=True)
class ReturnType:
    """
    Represents the return type of a function.

    Attributes:
        data_type: Return data type as a string
    """

    data_type: str


@dataclass(frozen=True)
class Signature:
    """
    Represents a function signature with parameters and return type.

    Attributes:
        params: List of function parameters
        returns: Function return type
    """

    params: List[Param]
    returns: ReturnType


@dataclass(frozen=True)
class ScalaUDFDef:
    """
    Complete definition for creating a Scala UDF in Snowflake.

    Contains all the information needed to generate the CREATE FUNCTION SQL statement
    and the Scala code body for the UDF.

    Attributes:
        name: UDF name
        signature: SQL signature (for Snowflake function definition)
        scala_signature: Scala signature (for Scala code generation)
        imports: List of JAR files to import
        null_handling: Null handling behavior (defaults to RETURNS_NULL_ON_NULL_INPUT)
    """

    name: str
    signature: Signature
    scala_signature: Signature
    imports: List[str]
    null_handling: NullHandling = NullHandling.RETURNS_NULL_ON_NULL_INPUT

    # -------------------- DDL Emitter --------------------

    def _gen_body_sql(self) -> str:
        """
        Generate the Scala code body for the UDF.

        Creates a Scala object that loads the serialized function from a binary file
        and provides a run method to execute it.

        Returns:
            String containing the complete Scala code for the UDF body
        """
        scala_return_type = self.scala_signature.returns.data_type
        # Convert Array to Seq for Scala compatibility in function signatures
        cast_scala_input_types = (
            ", ".join(p.data_type for p in self.scala_signature.params)
        ).replace("Array", "Seq")
        scala_arg_and_input_types_str = ", ".join(
            f"{p.name}: {p.data_type}" for p in self.scala_signature.params
        )
        scala_args_str = ", ".join(f"{p.name}" for p in self.scala_signature.params)
        return f"""import org.apache.spark.sql.connect.common.UdfPacket

import java.io.{{ByteArrayInputStream, ObjectInputStream}}
import java.nio.file.{{Files, Paths}}

object SparkUdf {{

  lazy val func: ({cast_scala_input_types}) => {scala_return_type} = {{
    val importDirectory = System.getProperty("com.snowflake.import_directory")
    val fPath = importDirectory + "{self.name}.bin"
    val bytes = Files.readAllBytes(Paths.get(fPath))
    val ois = new ObjectInputStream(new ByteArrayInputStream(bytes))
    try {{
      ois.readObject().asInstanceOf[UdfPacket].function.asInstanceOf[({cast_scala_input_types}) => {scala_return_type}]
    }} finally {{
      ois.close()
    }}
  }}

  def run({scala_arg_and_input_types_str}): {scala_return_type} = {{
    func({scala_args_str})
  }}
}}
"""

    def to_create_function_sql(self) -> str:
        """
        Generate the complete CREATE FUNCTION SQL statement for the Scala UDF.

        Creates a Snowflake CREATE OR REPLACE TEMPORARY FUNCTION statement with
        all necessary clauses including language, runtime version, packages,
        imports, and the Scala code body.

        Returns:
            Complete SQL DDL statement for creating the UDF
        """
        # self.validate()

        args = ", ".join(f"{p.name} {p.data_type}" for p in self.signature.params)
        ret_type = self.signature.returns.data_type

        def quote_single(s: str) -> str:
            """Helper function to wrap strings in single quotes for SQL."""
            return "'" + s + "'"

        # Handler and imports
        imports_sql = f"IMPORTS = ({', '.join(quote_single(x) for x in self.imports)})"

        return f"""
CREATE OR REPLACE TEMPORARY FUNCTION {self.name}({args})
RETURNS {ret_type}
LANGUAGE SCALA
{self.null_handling.value}
RUNTIME_VERSION = 2.12
PACKAGES = ('com.snowflake:snowpark:latest')
{imports_sql}
HANDLER = 'SparkUdf.run'
AS
$$
{self._gen_body_sql()}
$$;"""


def build_scala_udf_imports(session, payload, udf_name):
    """
    Build the list of imports needed for the Scala UDF.

    This function:
    1. Saves the UDF payload to a binary file in the session stage
    2. Collects user-uploaded JAR files from the stage
    3. Returns a list of all required JAR files for the UDF

    Args:
        session: Snowpark session
        payload: Binary payload containing the serialized UDF
        udf_name: Name of the UDF (used for the binary file name)

    Returns:
        List of JAR file paths to be imported by the UDF
    """
    # Save pciudf._payload to a bin file:
    import io

    payload_as_stream = io.BytesIO(payload)
    stage = session.get_session_stage()
    stage_resource_path = stage + RESOURCE_PATH
    closure_binary_file = stage_resource_path + "/" + udf_name + ".bin"
    session.file.put_stream(
        payload_as_stream,
        closure_binary_file,
        overwrite=True,
    )

    # Get a list of the jar files uploaded to the stage. We need to import the user's jar for the Scala UDF.
    res = session.sql(rf"LIST {stage}/ PATTERN='.*\.jar';").collect()
    user_jars = []
    for row in res:
        if RESOURCE_PATH not in row[0]:
            # Remove the stage path since it is not properly formatted.
            user_jars.append(row[0][row[0].find("/") :])
    # Format the user jars to be used in the IMPORTS clause of the stored procedure.
    return [
        closure_binary_file,
        f"{stage_resource_path}/spark-connect-client-jvm_2.12-3.5.6.jar",
        f"{stage_resource_path}/spark-common-utils_2.12-3.5.6.jar",
        f"{stage_resource_path}/spark-sql_2.12-3.5.6.jar",
        f"{stage_resource_path}/json4s-ast_2.12-3.7.0-M11.jar",
    ] + [f"{stage + jar}" for jar in user_jars]


def create_scala_udf(pciudf: ProcessCommonInlineUserDefinedFunction) -> ScalaUdf:
    """
    Create a Scala UDF in Snowflake from a ProcessCommonInlineUserDefinedFunction object.

    This function handles the complete process of creating a Scala UDF:
    1. Generates a unique function name if not provided
    2. Checks for existing UDFs in the session cache
    3. Creates the necessary imports list
    4. Maps types between different systems (Snowpark, Scala, Snowflake)
    5. Generates and executes the CREATE FUNCTION SQL statement

    If the UDF already exists in the session cache, it will be reused.

    Args:
        pciudf: The ProcessCommonInlineUserDefinedFunction object containing UDF details.

    Returns:
        A ScalaUdf object representing the created or cached Scala UDF.
    """
    from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session

    function_name = pciudf._function_name
    # If a function name is not provided, hash the binary file and use the first ten characters as the function name.
    if not function_name:
        import hashlib

        function_name = hashlib.sha256(pciudf._payload).hexdigest()[:10]
    udf_name = CREATE_SCALA_UDF_PREFIX + function_name

    session = get_or_create_snowpark_session()
    if udf_name in session._udfs:
        cached_udf = session._udfs[udf_name]
        return ScalaUdf(cached_udf.name, cached_udf.input_types, cached_udf.return_type)

    imports = build_scala_udf_imports(session, pciudf._payload, udf_name)

    def _build_params(
        pciudf: ProcessCommonInlineUserDefinedFunction,
        snowpark_type_mapper: Callable[[snowpark_type.DataType], str],
        spark_type_mapper: Callable[[types_proto.DataType], str],
    ) -> List[Param]:
        """
        Build the parameter list for the UDF signature.

        Args:
            pciudf: The UDF definition object
            mapper: Function to map Snowpark types to target type system

        Returns:
            List of Param objects representing the function parameters
        """
        if not pciudf._scala_input_types:
            return (
                [
                    Param(name=f"arg{i}", data_type=snowpark_type_mapper(input_type))
                    for i, input_type in enumerate(pciudf._input_types)
                ]
                if pciudf._input_types
                else []
            )
        else:
            return [
                Param(name=f"arg{i}", data_type=spark_type_mapper(input_type))
                for i, input_type in enumerate(pciudf._scala_input_types)
            ]

    # Create the Scala arguments and input types string: "arg0: Type0, arg1: Type1, ...".
    # In case the Scala UDF was created with `spark.udf.register`, the Spark Scala input types (from protobuf) are
    # stored in pciudf.scala_input_types.
    sql_input_params = _build_params(
        pciudf, map_snowpark_type_to_snowflake_type, map_spark_type_to_snowflake_type
    )
    sql_return_type = map_snowpark_type_to_snowflake_type(pciudf._return_type)
    scala_input_params = _build_params(
        pciudf, map_snowpark_type_to_scala_type, map_spark_type_to_scala_type
    )
    scala_return_type = map_snowpark_type_to_scala_type(pciudf._return_type)

    udf_def = ScalaUDFDef(
        name=udf_name,
        signature=Signature(
            params=sql_input_params, returns=ReturnType(sql_return_type)
        ),
        imports=imports,
        scala_signature=Signature(
            params=scala_input_params, returns=ReturnType(scala_return_type)
        ),
    )
    create_udf_sql = udf_def.to_create_function_sql()
    logger.info(f"Creating Scala UDF: {create_udf_sql}")
    session.sql(create_udf_sql).collect()
    return ScalaUdf(udf_name, pciudf._input_types, pciudf._return_type)


def map_snowpark_type_to_scala_type(t: snowpark_type.DataType) -> str:
    """
    Maps a Snowpark type to a Scala type string.

    Converts Snowpark DataType objects to their corresponding Scala type names.
    This mapping is used when generating Scala code for UDFs.

    Args:
        t: Snowpark DataType to convert

    Returns:
        String representation of the corresponding Scala type

    Raises:
        ValueError: If the Snowpark type is not supported
    """
    match type(t):
        case snowpark_type.ArrayType:
            return f"Array[{map_snowpark_type_to_scala_type(t.element_type)}]"
        case snowpark_type.BinaryType:
            return "Array[Byte]"
        case snowpark_type.BooleanType:
            return "Boolean"
        case snowpark_type.ByteType:
            return "Byte"
        case snowpark_type.DateType:
            return "java.sql.Date"
        case snowpark_type.DecimalType:
            return "java.math.BigDecimal"
        case snowpark_type.DoubleType:
            return "Double"
        case snowpark_type.FloatType:
            return "Float"
        case snowpark_type.GeographyType:
            return "Geography"
        case snowpark_type.IntegerType:
            return "Int"
        case snowpark_type.LongType:
            return "Long"
        case snowpark_type.MapType:  # can also map to OBJECT in Snowflake
            key_type = map_snowpark_type_to_scala_type(t.key_type)
            value_type = map_snowpark_type_to_scala_type(t.value_type)
            return f"Map[{key_type}, {value_type}]"
        case snowpark_type.NullType:
            return "String"  # cannot set the return type to Null in Snowpark Scala UDFs
        case snowpark_type.ShortType:
            return "Short"
        case snowpark_type.StringType:
            return "String"
        case snowpark_type.TimestampType:
            return "java.sql.Timestamp"
        case snowpark_type.VariantType:
            return "Variant"
        case _:
            raise ValueError(f"Unsupported Snowpark type: {t}")


def map_snowpark_type_to_snowflake_type(t: snowpark_type.DataType) -> str:
    """
    Maps a Snowpark type to a Snowflake type string.

    Converts Snowpark DataType objects to their corresponding Snowflake SQL type names.
    This mapping is used when generating CREATE FUNCTION SQL statements.

    Args:
        t: Snowpark DataType to convert

    Returns:
        String representation of the corresponding Snowflake type

    Raises:
        ValueError: If the Snowpark type is not supported
    """
    match type(t):
        case snowpark_type.ArrayType:
            return f"ARRAY({map_snowpark_type_to_snowflake_type(t.element_type)})"
        case snowpark_type.BinaryType:
            return "BINARY"
        case snowpark_type.BooleanType:
            return "BOOLEAN"
        case snowpark_type.ByteType:
            return "TINYINT"
        case snowpark_type.DateType:
            return "DATE"
        case snowpark_type.DecimalType:
            return "NUMBER"
        case snowpark_type.DoubleType:
            return "DOUBLE"
        case snowpark_type.FloatType:
            return "FLOAT"
        case snowpark_type.GeographyType:
            return "GEOGRAPHY"
        case snowpark_type.IntegerType:
            return "INT"
        case snowpark_type.LongType:
            return "BIGINT"
        case snowpark_type.MapType:
            # Maps to OBJECT in Snowflake if key and value types are not specified.
            key_type = map_snowpark_type_to_snowflake_type(t.key_type)
            value_type = map_snowpark_type_to_snowflake_type(t.value_type)
            return (
                f"MAP({key_type}, {value_type})"
                if key_type and value_type
                else "OBJECT"
            )
        case snowpark_type.NullType:
            return "VARCHAR"
        case snowpark_type.ShortType:
            return "SMALLINT"
        case snowpark_type.StringType:
            return "VARCHAR"
        case snowpark_type.TimestampType:
            return "TIMESTAMP"
        case snowpark_type.VariantType:
            return "VARIANT"
        case _:
            raise ValueError(f"Unsupported Snowpark type: {t}")


def map_spark_type_to_scala_type(t: types_proto.DataType) -> str:
    """
    Maps a Spark DataType (from protobuf) to a Scala type string.

    Converts Spark protobuf DataType objects to their corresponding Scala type names.
    This mapping is used when working with Spark Connect protobuf types.

    Args:
        t: Spark protobuf DataType to convert

    Returns:
        String representation of the corresponding Scala type

    Raises:
        ValueError: If the Spark type is not supported
    """
    match t.WhichOneof("kind"):
        case "array":
            return f"Array[{map_spark_type_to_scala_type(t.array.element_type)}]"
        case "binary":
            return "Array[Byte]"
        case "boolean":
            return "Boolean"
        case "byte":
            return "Byte"
        case "date":
            return "java.sql.Date"
        case "decimal":
            return "java.math.BigDecimal"
        case "double":
            return "Double"
        case "float":
            return "Float"
        case "integer":
            return "Int"
        case "long":
            return "Long"
        case "map":
            key_type = map_spark_type_to_scala_type(t.map.key_type)
            value_type = map_spark_type_to_scala_type(t.map.value_type)
            return f"Map[{key_type}, {value_type}]"
        case "null":
            return "String"  # cannot set the return type to Null in Snowpark Scala UDFs
        case "short":
            return "Short"
        case "string" | "char" | "varchar":
            return "String"
        case "timestamp" | "timestamp_ntz":
            return "java.sql.Timestamp"
        case _:
            raise ValueError(f"Unsupported Spark type: {t}")


def map_spark_type_to_snowflake_type(t: types_proto.DataType) -> str:
    """
    Maps a Spark DataType (from protobuf) to a Snowflake type string.

    Converts Spark protobuf DataType objects to their corresponding Snowflake SQL type names.
    This mapping is used when working with Spark Connect protobuf types in Snowflake UDFs.

    Args:
        t: Spark protobuf DataType to convert

    Returns:
        String representation of the corresponding Snowflake type

    Raises:
        ValueError: If the Spark type is not supported
    """
    match t.WhichOneof("kind"):
        case "array":
            return f"ARRAY({map_spark_type_to_snowflake_type(t.array.element_type)})"
        case "binary":
            return "BINARY"
        case "boolean":
            return "BOOLEAN"
        case "byte":
            return "TINYINT"
        case "date":
            return "DATE"
        case "decimal":
            return "NUMBER"
        case "double":
            return "DOUBLE"
        case "float":
            return "FLOAT"
        case "integer":
            return "INT"
        case "long":
            return "BIGINT"
        case "map":
            # Maps to OBJECT in Snowflake if key and value types are not specified.
            key_type = map_spark_type_to_snowflake_type(t.map.key_type)
            value_type = map_spark_type_to_snowflake_type(t.map.value_type)
            return (
                f"MAP({key_type}, {value_type})"
                if key_type and value_type
                else "OBJECT"
            )
        case "null":
            return "VARCHAR"
        case "short":
            return "SMALLINT"
        case "string" | "char" | "varchar":
            return "VARCHAR"
        case "timestamp" | "timestamp_ntz":
            return "TIMESTAMP"
        case _:
            raise ValueError(f"Unsupported Spark type: {t}")
