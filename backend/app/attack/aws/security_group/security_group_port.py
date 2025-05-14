import boto3

# 🔐 AWS 자격 증명 및 리전 (직접 하드코딩)
aws_access_key = ''
aws_secret_key = ''
region = "ap-northeast-2"

# EC2 클라이언트 생성
ec2 = boto3.client(
    'ec2',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=region
)

instances = ec2.describe_instances()

# 인스턴스 순회
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        print(f"\n[🔍] Instance: {instance_id}")

        for sg in instance['SecurityGroups']:
            sg_id = sg['GroupId']
            sg_name = sg['GroupName']
            print(f"   └─ 보안 그룹: {sg_name} ({sg_id})")

            # 보안 그룹의 인바운드 규칙 확인
            sg_detail = ec2.describe_security_groups(GroupIds=[sg_id])
            permissions = sg_detail['SecurityGroups'][0]['IpPermissions']

            already_open = False
            for perm in permissions:
                if (perm.get('FromPort') == 2375 and
                    perm.get('ToPort') == 2375 and
                    perm.get('IpProtocol') == 'tcp'):
                    for ip_range in perm.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            already_open = True

            if already_open:
                print("      [ℹ️] 2375 포트는 이미 열려 있음")
            else:
                try:
                    print("      [🛠️] 2375 포트 인바운드 규칙 추가 중...")
                    ec2.authorize_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': 2375,
                                'ToPort': 2375,
                                'IpRanges': [
                                    {'CidrIp': '0.0.0.0/0', 'Description': 'Allow Docker Remote'}
                                ]
                            }
                        ]
                    )
                    print("      [✅] 2375 포트 인바운드 열기 성공")
                except ec2.exceptions.ClientError as e:
                    print(f"      [❌] 에러 발생: {e}")