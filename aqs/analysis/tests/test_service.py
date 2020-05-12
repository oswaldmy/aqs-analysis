from aqs.analysis.service import run_dml_athena_query


class FakeAthenaClient:

    def __init__(self, QueryExecutionId: str):
        self.query_execution_id = QueryExecutionId

    def start_query_execution(self, QueryString: str, QueryExecutionContext: str, ResultConfiguration: Dict[str, Any]):
        self.query_sring = QueryString
        self.query_execution_context = QueryExecutionContext
        self.result_configuration = ResultConfiguration
        return {
            'QueryExecutionId': self.query_execution_id
        }

    def get_query_execution(self, QueryExecutionId: str):
        self.query_exec_id = self.query_execution_id
        random_state = random.choice(['QUEUED', 'RUNNING', 'SUCCEEDED'])
        random_encrypt_option = random.choice(['SSE_S3', 'SSE_KMS', 'CSE_KMS'])
        return {
                'QueryExecution': {
                    'QueryExecutionId': self.query_exec_id,
                    'Query': 'string',
                    'StatementType': 'DDL',
                    'ResultConfiguration': {
                        'OutputLocation': 'string',
                        'EncryptionConfiguration': {
                            'EncryptionOption': random_encrypt_option,
                            'KmsKey': 'string'
                        }
                    },
                    'QueryExecutionContext': {
                        'Database': 'string'
                    },
                    'Status': {
                        'State': random_state,
                        'StateChangeReason': 'string',
                        'SubmissionDateTime': datetime(2020, 5, 5),
                        'CompletionDateTime': datetime(2020, 5, 5)
                    },
                    'Statistics': {
                        'EngineExecutionTimeInMillis': 123,
                        'DataScannedInBytes': 123
                    }
                }
        }

    def get_query_results(self, QueryExecutionId: str, NextToken: str = '108c3cc98d12', MaxResults: int = 10):
        self.query_execution_id = QueryExecutionId
        self.next_token = NextToken
        self.max_results = MaxResults
        return {
            'UpdateCount': 123,
            'ResultSet': {
                'Rows': [
                    {
                        'Data': [
                            {'VarCharValue': 'year'},
                            {'VarCharValue': 'MeasureName'},
                        ]
                    },
                    {
                        'Data': [
                            {'VarCharValue': 2011},
                            {'VarCharValue': 'Number of days with maximum 8-hour average ozone concentration over the National Ambient Air Quality Standard'},
                        ]
                    },
                ],
                'ResultSetMetadata': {
                    'ColumnInfo': [
                        {
                            'CatalogName': 'testcase',
                            'SchemaName': 'testcase',
                            'TableName': 'testcase',
                            'Name': 'testcase',
                            'Label': 'testcase',
                            'Type': 'testcase',
                            'Precision': 123,
                            'Scale': 123,
                            'Nullable': 'NULLABLE',
                            'CaseSensitive': 'True'
                        },
                    ]
                }
            },
            'NextToken': '102364ys635'
        }


def test_run_dml_athena_query():
    database_name =  'aqs_vw_db'
    query = f"""SELECT StateName, MAX(CAST(Value AS DOUBLE))
            FROM {database_name}.{tablename}
            GROUP BY StateName
            """
    athena_client = FakeAthenaClient('ed98c98f-56b0ae69cca9')
    athena_query_results_location = "s3://vw-data-lab-etl/aqs-query-results/"

    query_status = run_dml_athena_query(query, database, athena_query_results_location, athena_client)
    assert query_status
