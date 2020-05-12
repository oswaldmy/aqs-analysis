from .service import transform_aqs_data, map_year_to_aqs_rows, save_results_to_s3

def handle(event, context):
    url = 'https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD'
    s3_bucket_name = 'vw-data-lab-etl'
    s3_object_folder = 'aqs-transformed'
    temp_output_location = '/tmp/aqs_temp_output.csv'
    transform_aqs_data(url, temp_output_location)
    year_rows = map_year_to_aqs_rows(temp_output_location)
    save_results_to_s3(year_rows, s3_object_folder, s3_bucket_name)
