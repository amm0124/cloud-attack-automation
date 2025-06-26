# python s3_delete.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --bucket-name my-bucket
import boto3
import argparse

def delete_s3_bucket(access_key, secret_key, region, bucket_name):
    """S3 버킷을 삭제하고 결과를 반환"""
    try:
        # boto3 클라이언트 생성
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 버킷 내 모든 객체 삭제
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_keys}
            )
            objects_deleted = len(delete_keys)
        else:
            objects_deleted = 0

        # 버킷 삭제
        s3.delete_bucket(Bucket=bucket_name)

        return f"""# S3 버킷 삭제 결과

## 버킷 정보
- **버킷 이름**: {bucket_name}
- **리전**: {region}
- **삭제된 객체 수**: {objects_deleted}개

## 결과
S3 버킷이 성공적으로 삭제되었습니다.
"""

    except Exception as e:
        return f"""# S3 버킷 삭제 실패

## 오류 정보
- **버킷 이름**: {bucket_name}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
S3 버킷 삭제에 실패했습니다.
"""

def main():
    parser = argparse.ArgumentParser(description='S3 버킷 삭제')
    parser.add_argument('--access-key', required=True, help='AWS Access Key')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
    parser.add_argument('--region', required=True, help='AWS Region')
    parser.add_argument('--bucket-name', required=True, help='S3 Bucket Name')
    parser.add_argument('--output-file', required=True, help='S3 Bucket Name')

    args = parser.parse_args()

    result = delete_s3_bucket(
        args.access_key,
        args.secret_key,
        args.region,
        args.bucket_name
    )

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print("S3 삭제 공격 완료.")

if __name__ == "__main__":
    main()