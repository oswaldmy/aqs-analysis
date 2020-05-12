from .service import run_ddl_queries, run_dml_queries

def handle(event, context):
    athena_input_dataset_location = "s3://vw-data-lab-etl/aqs-transformed/"
    athena_query_results_location = "s3://vw-data-lab-etl/aqs-query-results/"
    database_name = "aqs_vw_db"
    table_name = "aqs_analysis"
    run_ddl_queries(athena_input_dataset_location, athena_query_results_location, database_name, table_name)
    run_dml_queries(athena_query_results_location, database_name, table_name)

