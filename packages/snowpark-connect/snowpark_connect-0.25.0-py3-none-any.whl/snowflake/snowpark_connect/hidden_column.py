#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#


class HiddenColumn:
    """
    Represents a hidden column in a Snowflake table.

    Hidden columns are not visible in standard queries but can be accessed
    directly if needed. This class provides a way to reference such columns
    in Snowpark operations
    """

    def __init__(
        self,
        hidden_snowpark_name: str,
        spark_name: str,
        visible_snowpark_name: str,
        qualifiers: list[str] | None = None,
        original_position: int | None = None,
    ) -> None:
        """
        Initializes a HiddenColumn instance.

        Args:
            name (str): The name of the hidden column.
        """

        # The Snowpark internal name for the hidden column
        self.hidden_snowpark_name = hidden_snowpark_name
        # The Spark name for the hidden column
        self.spark_name = spark_name
        # The left side visible Snowpark name for the dropped right side column
        self.visible_snowpark_name = visible_snowpark_name
        # Qualifiers for the hidden column (e.g., table or schema names)
        self.qualifiers = qualifiers if qualifiers is not None else []
        # The position of the hidden column in the original schema
        self.original_position = original_position
