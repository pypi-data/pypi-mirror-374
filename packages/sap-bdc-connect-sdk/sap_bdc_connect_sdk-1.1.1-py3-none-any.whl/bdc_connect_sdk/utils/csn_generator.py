# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
from typing import Any
from pyspark.sql import SparkSession
from bdc_connect_sdk import __version__, __package__
import re
import pandas

def add_backticks(s: str) -> str:
    return ".".join(f"`{item}`" for item in s.split("."))

def get_table_column_mapping(full_table_name: str, spark: SparkSession) -> dict[str, Any]:
    """
    Retrieves the column mapping for a given table in a Spark environment.

    This function processes the table schema and maps Spark data types to 
    Cloud Data Services (CDS) compatible data types. It returns a dictionary 
    where the key is the column name and the value is a dictionary containing 
    the data type and any additional attributes like precision, scale, or 
    primary/foreign key status.

    Parameters:
    - full_table_name (str): The fully qualified name of the table.
    - spark: The Spark session used to execute SQL commands.

    Returns:
    - dict: A dictionary mapping column names to their respective type and attributes.
    
    Note:
    - Handles primary and foreign key constraints where present.
    - The schema description extracted to the variable schema_list will have a structure like:
      [['column_name', 'data_type', 'None'], 
       ['column_name', 'data_type', 'None'], 
       ['column_name', 'data_type', 'None'], 
       ['', '', ''], 
       ['# Constraints', '', ''], 
       ['pk', 'PRIMARY KEY(`column_name`)', ''], 
       ['fk', 'FOREIGN KEY(`column_name`)', '']]
    """
    
    spark_csn_mapping = {
        "boolean": "cds.Boolean",
        "string": "cds.String",
        "int": "cds.Integer",
        "double": "cds.Double",
        "bigint": "cds.Integer64",
        "decimal": "cds.Decimal",
        "date": "cds.Date",
        "timestamp": "cds.DateTime",
        "timestamp_ms": "cds.Timestamp"
    }

    # Configure pandas to be able to show the whole object in DESCRIBE TABLE EXTENDED
    pandas.set_option('display.max_colwidth', None)  # Don't truncate column values
    pandas.set_option('display.max_columns', None)   # Show all columns
    pandas.set_option('display.max_rows', None)      # Show all rows

    schema_sql = f"DESCRIBE TABLE EXTENDED {add_backticks(full_table_name)}"
    schema_description = spark.sql(schema_sql).toPandas() #type: ignore
    schema_list = schema_description.values.tolist()

    column_mapping: dict[str, Any] = {}
    is_column_section = True
    is_constraints_section = False
    for column_name, data_type, _ in schema_list:
        # if the array is ['', '', ''], it means the column section is over
        if not column_name and not data_type:
            is_column_section = False
            is_constraints_section = False
            continue

        # if the array is ['# Constraints', '', ''], it means the constraints section is beginning
        if "Constraints" in column_name:
            is_constraints_section = True
            continue

        if is_column_section:
            if "decimal" in data_type:
                schema_key = data_type.split("(")[0]
                precision, scale = re.findall(r"\d+", data_type)
                base_dtype = spark_csn_mapping[schema_key]
                column_mapping[column_name] = {"type": base_dtype, "precision": int(precision), "scale": int(scale)}
            elif "string" in data_type:
                schema_key = "string"
                base_dtype = spark_csn_mapping[schema_key]
                column_mapping[column_name] = {"type": base_dtype, "length": 5000}
            elif "float" in data_type:
                raise TypeError("Unsupported data type(float): consider data type `Double`.")
            else:
                csn_dtype = spark_csn_mapping[data_type]
                column_mapping[column_name] = {"type": csn_dtype}
        
        if is_constraints_section:
            if "PRIMARY" in data_type or "FOREIGN" in data_type:
                # this split is to get the column name from PRIMARY/FOREIGN KEY(`column_name`)
                columns = re.findall(r'`([^`]+)`', data_type)

                for col in columns:
                    column_mapping[col]["key"] = True

    return column_mapping

def generate_csn_template(share_name: str):
    """
    Generates a CSN (Core Schema Notation) schema file for each table and schema within a specified data share.

    This function retrieves information about tables and schemas in a given delta share, maps their structures 
    to CSN-compliant schemas, and saves these schemas as JSON files. 

    Parameters:
    - share_name (str): Name of the share to be generated the csn

    Process Overview:
    1. Establish a Spark session to query metadata about the data structures in the share.
    2. For each table within the specified share:
       a. Extract the column mapping and metadata.
       b. Define a CSN schema for the table.
    3. For each schema in the share:
       a. Enumerate its tables and repeat step 4 for each table.
    4. Write the generated CSN definition to a JSON file, named according to the share.

    Output:
    - JSON files conforming to CSN format, each describing the structure of tables and schemas in the specified share.

    Note:
    - The CSN format is tailored for use with delta sharing infrastructure.
    """

    spark = SparkSession.builder.appName("ORD_CSN_Generation").getOrCreate()
    delta_share_sql = f"SHOW ALL IN SHARE {add_backticks(share_name)}"
    delta_share_information = spark.sql(delta_share_sql).toPandas().to_dict("records") #type: ignore

    csn_schema: dict[str, Any] = {
        "csnInteropEffective": "1.0",
        "$schema": "2.0",
        "definitions": {
        },
        "i18n": {},
        "meta": {
            "creator": f"{str(__package__)}-{str(__version__)}",
            "flavor": "inferred"
        }
    }

    for schema_asset in delta_share_information:
        if schema_asset["type"] == "TABLE":
            schema_name = schema_asset["name"].split(".")[0]
            table_name = schema_asset["name"]
            full_table_name = schema_asset["shared_object"]

            column_mapping = get_table_column_mapping(full_table_name, spark)
            csn_schema["definitions"][schema_name] = {"kind": "context"}
            csn_schema["definitions"][table_name] = {"kind": "entity"}
            csn_schema["definitions"][table_name]["elements"] = column_mapping

        elif schema_asset["type"] == "SCHEMA":
            schema_name = schema_asset["name"]
            full_schema_name = schema_asset["shared_object"]
            
            csn_schema["definitions"][schema_name] = {"kind": "context"}
            
            tables_sql = f"SHOW TABLES IN {add_backticks(full_schema_name)}"
            tables_df = spark.sql(tables_sql).toPandas() #type: ignore
            for _, row in tables_df.iterrows():
                table_name = f"{schema_name}.{row['tableName']}"
                full_table_name = f"{full_schema_name}.{row['tableName']}"
        
                column_mapping = get_table_column_mapping(full_table_name, spark)
                csn_schema["definitions"][table_name] = {"kind": "entity"}
                csn_schema["definitions"][table_name]["elements"] = column_mapping

    return csn_schema

# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
