import boto3
import time
from datetime import datetime


def run_dml_athena_query(query: str, database: str, athena_result_bucket: str, athena_client=None):
    athena_client = athena_client if athena_client else boto3.client('athena')
    query_execution_id = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': athena_result_bucket,
        }
    )['QueryExecutionId']
    if(_is_athena_query_successful(query_execution_id)):
        query_result = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    try:
        print(query_result['ResultSet']['Rows'])
    except IndexError:
        print(f"Cannot retrieve results at specified index")
    return True


# 1. Sum value of "Number of days with maximum 8-hour average ozone concentration
# over the National Ambient Air Quality Standard" per year
def sum_value_by_year(database_name: str, tablename: str) -> str:
    measurename  = "Number of days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard"
    return f"""SELECT year, MeasureName, SUM(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            WHERE MeasureName = '{measurename}'
            GROUP BY year, MeasureName
            """


# 2. Year with max value of "Number of days with maximum 8-hour average ozone concentration
# over the National Ambient Air Quality Standard" from year 2008 and later (inclusive)
def max_value_from_2008(database_name: str, tablename: str) -> str:
    measurename  = "Number of days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard"
    return f"""SELECT year, MeasureName, MAX(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            WHERE MeasureName = '{measurename}'
            AND year >= 2008
            GROUP BY year, MeasureName
            """


# 3. Max value of each measurement per state
def max_value_per_state(database_name: str, tablename: str) -> str:
    return f"""SELECT StateName, MAX(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            GROUP BY StateName
            """


# 4. Average value of "Number of person-days with PM2.5
# over the National Ambient Air Quality Standard (monitor and modeled data)"
# per year and state in ascending order
def average_value_per_year_and_state(database_name: str, tablename: str) -> str:
    measurename = "Number of person-days with PM2.5 over the National Ambient Air Quality Standard (monitor and modeled data)"
    return f"""SELECT year, StateName, AVG(CAST(Value AS DOUBLE)) AS Average
            FROM {database_name}.{tablename}
            WHERE MeasureName = '{measurename}'
            GROUP BY year, StateName
            ORDER BY Average ASC
            """


# 5. State with the max accumulated value of "Number of days with maximum 8-hour average
# ozone concentration over the National Ambient Air Quality Standard" overall years
def max_value_by_state(database_name: str, tablename: str) -> str:
    measurename = "Number of days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard"
    return f"""
    SELECT StateName, MAX(states_sum) AS StatesMaxSum
    FROM (SELECT StateName, SUM(CAST(Value AS DOUBLE)) AS states_sum
                FROM {database_name}.{tablename}
                WHERE MeasureName = '{measurename}'
                GROUP BY StateName)
    GROUP BY StateName
    ORDER BY StatesMaxSum DESC
    """

# 6. Average value of "Number of person-days with maximum 8-hour average ozone concentration
# over the National Ambient Air Quality Standard" in the state of Florida
def average_value_in_florida(database_name: str, tablename: str) -> str:
    measurename = "Number of person-days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard"
    return f"""SELECT StateName, AVG(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            WHERE MeasureName = '{measurename}'
            AND StateName = 'Florida'
            GROUP BY StateName
            """


# 7. County with min "Number of days with maximum 8-hour average ozone concentration over
# the National Ambient Air Quality Standard" per state per year
def county_with_min_value_per_state_and_year(database_name: str, tablename: str) -> str:
    measurename = "Number of days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard"
    return f"""SELECT year, StateName, CountyName, MIN(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            WHERE MeasureName = '{measurename}'
            GROUP BY year, StateName, CountyName
            """


def create_db_table_query(athena_input_dataset_location: str, database_name: str, table_name: str):
    create_database_query = "CREATE DATABASE IF NOT EXISTS %s;" % (database_name)
    create_table_query = \
        """CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
        `Index` string,
        `MeasureId` string,
        `MeasureName` string,
        `MeasureType` string,
        `StratificationLevel` string,
        `StateFips` string,
        `StateName` string,
        `CountyFips` string,
        `CountyName` string,
        `ReportYear` string,
        `Value` string,
        `Unit` string,
        `UnitName` string,
        `DataOrigin` string,
        `MonitorOnly` string
    ) PARTITIONED BY (`year` int)
      ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
      WITH SERDEPROPERTIES (
        'serialization.format' = ',',
        'field.delim' = ','
    )
    LOCATION '%s'
    TBLPROPERTIES ('has_encrypted_data'='false');""" % (database_name, table_name, athena_input_dataset_location )
    return create_database_query, create_table_query


def _is_athena_query_successful(query_execution_id: str, athena_client=None) -> bool:
     athena_client = athena_client if athena_client else boto3.client('athena')
     query_status = None
     while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
        query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)['QueryExecution']['Status']['State']
        if query_status == 'FAILED' or query_status == 'CANCELLED':
            print(f"Query with execution id: {query_execution_id} FAILED or was CANCELLED.")
            raise Exception(f"Athena query with execution id: {query_execution_id} Failed or was Cancelled.")
     return True


def athena_ddl_query(query: str, database_name: str, athena_results_location: str, athena_client=None):
    athena_client = athena_client if athena_client else boto3.client('athena')
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database_name
            },
        ResultConfiguration={
            'OutputLocation': athena_results_location,
            }
        )
    if(_is_athena_query_successful(response['QueryExecutionId'])):
        print('Execution ID: ' + response['QueryExecutionId'])


def load_athena_partitions(database_name: str, table_name: str):
    return f'MSCK REPAIR TABLE {database_name}.{table_name};'


def run_ddl_queries(athena_input_dataset_location: str, athena_query_results_location: str, database_name: str, table_name: str):
    create_db_query, create_table_query = create_db_table_query(athena_input_dataset_location, database_name, table_name)
    queries = [create_db_query, create_table_query]
    for query in queries:
        print(f"Executing query: {query}")
        athena_ddl_query(query, database_name, athena_query_results_location)


def run_dml_queries(athena_results_location: str, database_name: str, table_name: str):
    load_partitions_query = load_athena_partitions(database_name, table_name)
    sum_value_by_year_query = sum_value_by_year(database_name, table_name)
    max_value_from_2008_query = max_value_from_2008(database_name, table_name)
    max_value_per_state_query = max_value_per_state(database_name, table_name)
    average_value_per_year_and_state_query = average_value_per_year_and_state(database_name, table_name)
    max_value_by_state_query = max_value_by_state(database_name, table_name)
    average_value_in_florida_query = average_value_in_florida(database_name, table_name)
    county_with_min_value_per_state_and_year_query = county_with_min_value_per_state_and_year(database_name, table_name)
    queries = [
        load_partitions_query,
        sum_value_by_year_query,
        max_value_from_2008_query,
        max_value_per_state_query,
        average_value_per_year_and_state_query,
        max_value_by_state_query,
        average_value_in_florida_query,
        county_with_min_value_per_state_and_year_query
    ]
    for query in queries:
        print(f"Executing query: {query}")
        run_dml_athena_query(query, database_name, athena_results_location)
