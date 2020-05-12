import csv
import requests
import json
import boto3
import pandas as pd
import uuid
from collections import defaultdict
from typing import Dict, List, Any
from io import StringIO


def transform_aqs_data(url: str, temp_output_location: str) -> str:
    s3_client = boto3.client('s3')
    response = requests.get(url)
    response_content = response.content
    aqs_data_rows = pd.DataFrame([json.loads(response_content)])['data'][0]
    rows_df = pd.DataFrame(aqs_data_rows)
    cleaned_df = rows_df.drop(rows_df.columns[[0, 1, 2, 3, 4, 5, 6, 7]], axis=1)
    cleaned_df.columns =["MeasureId","MeasureName","MeasureType","StratificationLevel","StateFips","StateName","CountyFips","CountyName","ReportYear","Value","Unit","UnitName","DataOrigin","MonitorOnly"]
    cleaned_df.to_csv(temp_output_location, encoding='utf-8')


def map_year_to_aqs_rows(temp_aqs_results_path: str = '/tmp/aqs_temp_output.csv') -> Dict[str, Any]:
    year_rows = {}
    with open(temp_aqs_results_path) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(reader, None)
        for row in reader:
            if row[9] in year_rows:
                year_rows[row[9]].append(row)
            else:
                year_rows[row[9]] = [row]
    return year_rows


def _csv_output_columns() -> List[str]:
    return ['MeasureId','MeasureName',
            'MeasureType','StratificationLevel',
            'StateFips','StateName','CountyFips',
            'CountyName','ReportYear','Value',
            'Unit','UnitName','DataOrigin','MonitorOnly'
            ]


def save_results_to_s3(year_mapped_rows: Dict[str, Any], object_folder: str, s3_bucket_name: str):
    s3_client = boto3.client('s3')
    for year, rows in year_mapped_rows.items():
        object_name = str(uuid.uuid4()) + '.csv'
        object_output_path = f'{object_folder}/year={year}/{object_name}'
        rows_to_df = pd.DataFrame.from_records(rows)
        rows_to_df.drop([0], inplace=True, axis=1)
        csv_buffer = StringIO()
        rows_to_df.to_csv(csv_buffer, header=True, columns=csv_output_columns())
        content = csv_buffer.getvalue()
        s3_client.put_object(Bucket=s3_bucket_name, Key=object_output_path, Body=content)
        print(f"successfully written output to s3 path: s3://{s3_bucket_name}/{object_output_path}")


