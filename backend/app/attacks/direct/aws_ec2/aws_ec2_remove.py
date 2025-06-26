# python s3_delete.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region ap-northeast-2 --bucket-name my-bucket


import boto3
import argparse

def terminate_ec2_instance(access_key, secret_key, region, instance_id):
   """EC2 인스턴스를 삭제하고 결과를 반환"""
   try:
       # boto3 클라이언트 생성
       ec2 = boto3.client(
           'ec2',
           aws_access_key_id=access_key,
           aws_secret_access_key=secret_key,
           region_name=region
       )

       # EC2 인스턴스 삭제
       response = ec2.terminate_instances(InstanceIds=[instance_id])

       # 결과 생성
       terminating_instance = response['TerminatingInstances'][0]
       current_state = terminating_instance['CurrentState']['Name']
       previous_state = terminating_instance['PreviousState']['Name']

       return f"""# EC2 인스턴스 삭제 결과

## 인스턴스 정보
- **인스턴스 ID**: {instance_id}
- **리전**: {region}

## 상태 변경
- **이전 상태**: {previous_state}
- **현재 상태**: {current_state}

## 결과
EC2 인스턴스가 성공적으로 삭제되었습니다.
"""

   except Exception as e:
       return f"""# EC2 인스턴스 삭제 실패

## 오류 정보
- **인스턴스 ID**: {instance_id}
- **리전**: {region}
- **오류 메시지**: {str(e)}

## 결과
EC2 인스턴스 삭제에 실패했습니다.
"""

def main():
   parser = argparse.ArgumentParser(description='EC2 인스턴스 삭제')
   parser.add_argument('--access-key', required=True, help='AWS Access Key')
   parser.add_argument('--secret-key', required=True, help='AWS Secret Key')
   parser.add_argument('--region', required=True, help='AWS Region')
   parser.add_argument('--instance-id', required=True, help='EC2 Instance ID')
   parser.add_argument('--output-file', default='ec2_terminate_result.md', help='출력 파일 경로')
   args = parser.parse_args()

   result = terminate_ec2_instance(
       args.access_key,
       args.secret_key,
       args.region,
       args.instance_id
   )

   with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(result)

   print("공격 수행 완료.")

if __name__ == "__main__":
   main()

