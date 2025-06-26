# python lambda_delete.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --function-name my-function


import boto3
import argparse

def delete_lambda_function(access_key, secret_key, region, function_name):
    """Lambda 함수를 삭제하고 결과를 반환"""
    try:
        # boto3 클라이언트 생성
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 함수 정보 확인
        function_info = lambda_client.get_function(FunctionName=function_name)
        function_arn = function_info['Configuration']['FunctionArn']
        runtime = function_info['Configuration']['Runtime']

        # Lambda 함수 삭제
        lambda_client.delete_function(FunctionName=function_name)

        return f"""# Lambda 함수 삭제 결과

## 함수 정보
- **함수 이름**: {function_name}
- **함수 ARN**: {function_arn}
- **런타임**: {runtime}
- **리전**: {region}

## 결과
Lambda 함수가 성공적으로 삭제되었습니다.
"""

    except Exception as e:
        return f"""# Lambda 함수 삭제 실패

## 오류 정보
- **함수 이름**: {function_name}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
Lambda 함수 삭제에 실패했습니다.
"""

def main():
    parser = argparse.ArgumentParser(description='Lambda 함수 삭제')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--function-name', required=True, help='Lambda Function Name')
    parser.add_argument('--output-file', default='markdown', help='Output format (default: markdown)')
    args = parser.parse_args()

    result = delete_lambda_function(
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name
    )
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print("lambda 삭제 완료.")

if __name__ == "__main__":
    main()