import boto3
import argparse
import zipfile
import os
import datetime
from pathlib import Path


def upload_file_to_lambda(access_key, secret_key, region, function_name, file_path):
    """지정된 파일을 Lambda 함수로 업로드"""
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    try:
        # 기존 함수 정보 백업
        original_function = lambda_client.get_function(FunctionName=function_name)

        # 파일을 ZIP으로 압축
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Lambda 함수 코드 업데이트
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=file_content
        )

        return {
            'success': True,
            'original_function': original_function,
            'updated_function': response,
            'file_size': len(file_content)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_report(result, access_key, secret_key, region, function_name, file_path, report_name=None):
    """마크다운 보고서 생성"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# Lambda Function Upload Report

## Basic Information
- Target Function: {function_name}
- AWS Region: {region}
- Upload Time: {timestamp}
- Source File: {os.path.basename(file_path)}

## Upload Results
"""

    if result['success']:
        original = result['original_function']['Configuration']
        updated = result['updated_function']

        report += f"""### Success
- Status: Upload completed successfully
- File Size: {result['file_size']} bytes
- Original Code Size: {original['CodeSize']} bytes
- Updated Code Size: {updated['CodeSize']} bytes
- Original SHA256: {original['CodeSha256']}
- Updated SHA256: {updated['CodeSha256']}

### Function Configuration
- Runtime: {original['Runtime']}
- Handler: {original['Handler']}
- Timeout: {original['Timeout']} seconds
- Memory: {original['MemorySize']} MB
- Last Modified: {original['LastModified']}

### Access Details
- Function ARN: {original['FunctionArn']}
- Role ARN: {original['Role']}

## Impact Assessment
- Code replacement: Complete
- Function availability: Maintained
- Configuration changes: None
"""
    else:
        report += f"""### Failed
- Status: Upload failed
- Error: {result['error']}
- Function state: Unchanged
"""

    # 보고서 저장
    if report_name:
        report_filename = report_name if report_name.endswith('.md') else f"{report_name}.md"
    else:
        report_filename = f"lambda_upload_report_{function_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)

    return report_filename


def main():
    parser = argparse.ArgumentParser(description='Upload file to Lambda function and generate report')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--function-name', required=True, help='Lambda Function Name')
    parser.add_argument('--file', required=True, help='File to upload')
    parser.add_argument('--output', help='Report filename (optional)')

    args = parser.parse_args()

    # 파일 존재 확인
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found")
        return

    print(f"Starting upload to Lambda function: {args.function_name}")
    print(f"Source file: {args.file}")
    print(f"Region: {args.region}")

    # 파일 업로드 실행
    result = upload_file_to_lambda(
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name,
        args.file
    )

    # 보고서 생성
    report_file = generate_report(
        result,
        args.access_key,
        args.secret_key,
        args.region,
        args.function_name,
        args.file,
        args.output
    )

    if result['success']:
        print("Upload completed successfully")
    else:
        print(f"Upload failed: {result['error']}")

    print(f"Report generated: {report_file}")


if __name__ == "__main__":
    main()