# python s3_suspend.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --bucket-name my-bucket

import boto3
import argparse

def suspend_s3_versioning(access_key, secret_key, region, bucket_name):
    """S3 버킷 버저닝을 비활성화하고 결과를 반환"""
    try:
        # boto3 클라이언트 생성
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 현재 버저닝 상태 확인
        current_versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        current_status = current_versioning.get('Status', 'Disabled')

        # 버저닝 비활성화
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Suspended'}
        )

        return f"""# S3 버킷 버저닝 비활성화 결과

## 버킷 정보
- **버킷 이름**: {bucket_name}
- **리전**: {region}

## 상태 변경
- **이전 상태**: {current_status}
- **현재 상태**: Suspended

## 결과
S3 버킷 버저닝이 성공적으로 비활성화되었습니다.
"""

    except Exception as e:
        return f"""# S3 버킷 버저닝 비활성화 실패

## 오류 정보
- **버킷 이름**: {bucket_name}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
S3 버킷 버저닝 비활성화에 실패했습니다.
"""

def main():
    parser = argparse.ArgumentParser(description='S3 버킷 버저닝 비활성화')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--bucket-name', required=True, help='S3 Bucket Name')

    args = parser.parse_args()

    result = suspend_s3_versioning(
        args.access_key,
        args.secret_key,
        args.region,
        args.bucket_name
    )

    print(result)

if __name__ == "__main__":
    main()