import boto3
import time
import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import ssh

def add_ssh_key(aws_access_key, aws_secret_key, aws_region, ec2_instance_id, new_keypair_name):
    """새 SSH 키 생성하고 EC2에 추가"""

    # AWS 클라이언트
    ec2 = boto3.client('ec2', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    ssm = boto3.client('ssm', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    print("🔑 새 SSH 키 생성 중...")

    # 1. AWS에서 키페어 생성
    try:
        import os
        response = ec2.create_key_pair(KeyName=new_keypair_name, KeyType='rsa')
        private_key = response['KeyMaterial']

        output_dir = "/Users/geonho/workspace/cloud-attack-automation/backend/app/report"
        pem_path = os.path.join(output_dir, f"{new_keypair_name}.pem")

        # 로컬에 저장
        with open(pem_path, 'w') as f:
            f.write(private_key)



        print(f"   ✅ 키 생성됨: {new_keypair_name}")

        # 퍼블릭 키 추출
        key_obj = serialization.load_pem_private_key(private_key.encode(), password=None)
        public_key = ssh.serialize_ssh_public_key(key_obj.public_key()).decode().strip()

        # 코멘트 추가
        public_key_line = f"{public_key} {new_keypair_name}"

    except Exception as e:
        print(f"   ❌ 키 생성 실패: {e}")
        return False

    print("📡 EC2에 키 추가 중...")

    # 2. SSM으로 키 추가
    try:
        command = f'''
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "{public_key_line}" >> /home/ubuntu/.ssh/authorized_keys
chmod 600 /home/ubuntu/.ssh/authorized_keys
echo "키 추가 완료"
cat /home/ubuntu/.ssh/authorized_keys | wc -l
'''

        response = ssm.send_command(
            InstanceIds=[ec2_instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command.strip()]}
        )

        # 결과 확인
        time.sleep(5)
        result = ssm.get_command_invocation(
            CommandId=response['Command']['CommandId'],
            InstanceId=ec2_instance_id
        )

        if result['Status'] == 'Success':
            output = result.get('StandardOutputContent', '')
            print(f"   ✅ 키 추가 성공!")
            print(f"   📄 결과: {output}")
            print(f"\n🎉 접속 명령:")
            print(f"   ssh -i {new_keypair_name}.pem ubuntu@YOUR_EC2_IP")
            return True
        else:
            print(f"   ❌ 실패: {result['Status']}")
            print(f"   📝 에러: {result.get('StandardErrorContent', '')}")
            return False

    except Exception as e:
        print(f"   ❌ SSM 명령 실패: {e}")
        return False

def check_keys(aws_access_key, aws_secret_key, aws_region, ec2_instance_id):
    """현재 등록된 키 확인"""

    ssm = boto3.client('ssm', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    try:
        response = ssm.send_command(
            InstanceIds=[ec2_instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': ['cat /home/ubuntu/.ssh/authorized_keys']}
        )

        time.sleep(3)
        result = ssm.get_command_invocation(
            CommandId=response['Command']['CommandId'],
            InstanceId=ec2_instance_id
        )

        print("📋 현재 등록된 키들:")
        print(result.get('StandardOutputContent', ''))

    except Exception as e:
        print(f"키 확인 실패: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='EC2에 새 SSH 키 추가')
    parser.add_argument('--access-key', required=True, help='AWS Access Key ID')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('--region', required=True, help='AWS Region (예: ap-northeast-2)')
    parser.add_argument('--instance-id', required=True, help='EC2 Instance ID (예: i-1234567890abcdef0)')
    parser.add_argument('--keypair-name', required=True, help='새로 생성할 키페어 이름')

    args = parser.parse_args()

    print("🚀 SSH 키 추가 시작\n")

    # 현재 키 상태 확인
    print("1. 현재 상태 확인")
    check_keys(args.access_key, args.secret_key, args.region, args.instance_id)

    print("\n2. 새 키 추가")
    if add_ssh_key(args.access_key, args.secret_key, args.region, args.instance_id, args.keypair_name):
        print("\n3. 추가 후 상태 확인")
        check_keys(args.access_key, args.secret_key, args.region, args.instance_id)
    else:
        print("\n❌ 키 추가 실패")