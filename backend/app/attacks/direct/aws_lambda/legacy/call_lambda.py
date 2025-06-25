import boto3
import json
import argparse

def invoke_lambda(access_key, secret_key, region, function_name, payload):
    client = boto3.client(
        'lambda',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload).encode()
    )

    response_payload = response['Payload'].read()
    print("Lambda response:", response_payload.decode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invoke an AWS Lambda function with JSON payload.")
    parser.add_argument("--access_key", required=True, help="AWS Access Key")
    parser.add_argument("--secret_key", required=True, help="AWS Secret Key")
    parser.add_argument("--region", required=True, help="AWS Region (e.g., us-east-1)")
    parser.add_argument("--function_name", required=True, help="Lambda function name")
    parser.add_argument("--payload", required=False, help="JSON string payload (default: '{}')", default='{}')

    args = parser.parse_args()

    try:
        payload_dict = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print("Invalid JSON for --payload:", e)
        exit(1)

    invoke_lambda(
        access_key=args.access_key,
        secret_key=args.secret_key,
        region=args.region,
        function_name=args.function_name,
        payload=payload_dict
    )
"""

python invoke_lambda_cli.py \
  --access_key YOUR_ACCESS_KEY \
  --secret_key YOUR_SECRET_KEY \
  --region us-east-1 \
  --function_name my-lambda-function \
  --payload '{"key": "value", "count": 3}'
  """