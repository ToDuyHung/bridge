import asyncio
import os
import time
import json
from mcp.server.fastmcp import FastMCP
import boto3
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("athena-mcp-server")

# AWS Config placeholder
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "mock_database")
ATHENA_OUTPUT_LOCATION = os.getenv("ATHENA_OUTPUT_LOCATION", "s3://mock-bucket/athena-results/")

# Initialize boto3 client if we have real credentials, otherwise mock it
athena_client = None
if os.getenv("AWS_ACCESS_KEY_ID"):
    athena_client = boto3.client('athena', region_name=AWS_REGION)

@mcp.tool()
def query_athena_sql(sql_query: str) -> str:
    """
    Execute a SQL query against AWS Athena to retrieve data from the Data Lake.
    
    Args:
        sql_query: The SQL query string to execute.
    """
    if not athena_client:
        # Return mock data for PoC when no real AWS credentials are provided
        mock_response = [
            {"Date": "2023-01-01", "Revenue": 1500, "Users": 120},
            {"Date": "2023-01-02", "Revenue": 1800, "Users": 140},
            {"Date": "2023-01-03", "Revenue": 1650, "Users": 130},
            {"Date": "2023-01-04", "Revenue": 2100, "Users": 160},
        ]
        return json.dumps({"status": "success", "mock": True, "data": mock_response}, indent=2)

    try:
        # Start Query Execution
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            QueryExecutionContext={'Database': ATHENA_DATABASE},
            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION}
        )
        query_execution_id = response['QueryExecutionId']

        # Wait for query to complete
        while True:
            state_response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = state_response['QueryExecution']['Status']['State']
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(1)

        if state != 'SUCCEEDED':
            return json.dumps({"status": "error", "message": f"Query {state}"})

        # Get Results
        results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        # Parse Athena results into JSON array of dicts
        rows = results_response['ResultSet']['Rows']
        if not rows:
            return json.dumps({"status": "success", "data": []})

        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        parsed_data = []
        for row in rows[1:]:
            values = [col.get('VarCharValue', None) for col in row['Data']]
            parsed_data.append(dict(zip(columns, values)))

        return json.dumps({"status": "success", "data": parsed_data}, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run()
