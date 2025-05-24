import boto3
import argparse
from datetime import datetime


def create_aws_session(access_key, secret_key, region):
    """AWS 세션 생성"""
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


def get_account_info(session):
    """계정 정보 조회"""
    try:
        sts = session.client('sts')
        return sts.get_caller_identity()
    except Exception as e:
        return {"error": str(e)}


def analyze_ec2_instances(ec2):
    """EC2 인스턴스 분석"""
    instances = []
    try:
        response = ec2.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'public_ip': instance.get('PublicIpAddress', 'N/A'),
                    'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                    'vpc_id': instance.get('VpcId', 'N/A'),
                    'subnet_id': instance.get('SubnetId', 'N/A'),
                    'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                    'key_name': instance.get('KeyName', 'N/A'),
                    'public_dns': instance.get('PublicDnsName', 'N/A')
                })
    except Exception as e:
        return [{"error": str(e)}]

    return instances


def analyze_security_groups(ec2):
    """보안 그룹 분석"""
    security_groups = []
    high_risk_groups = []

    try:
        response = ec2.describe_security_groups()
        for sg in response['SecurityGroups']:
            sg_info = {
                'id': sg['GroupId'],
                'name': sg['GroupName'],
                'description': sg['Description'],
                'vpc_id': sg.get('VpcId', 'N/A'),
                'inbound_rules': [],
                'outbound_rules': [],
                'risk_level': 'low'
            }

            # 인바운드 규칙 분석
            for rule in sg['IpPermissions']:
                rule_info = analyze_sg_rule(rule, 'inbound')
                sg_info['inbound_rules'].append(rule_info)
                if rule_info['risk_level'] == 'high':
                    sg_info['risk_level'] = 'high'

            # 아웃바운드 규칙 분석
            for rule in sg['IpPermissionsEgress']:
                rule_info = analyze_sg_rule(rule, 'outbound')
                sg_info['outbound_rules'].append(rule_info)
                if rule_info['risk_level'] == 'high' and sg_info['risk_level'] != 'high':
                    sg_info['risk_level'] = 'medium'

            security_groups.append(sg_info)
            if sg_info['risk_level'] == 'high':
                high_risk_groups.append(sg_info)

    except Exception as e:
        return [{"error": str(e)}], []

    return security_groups, high_risk_groups


def analyze_sg_rule(rule, direction):
    """보안 그룹 규칙 분석"""
    protocol = rule.get('IpProtocol', 'N/A')
    from_port = rule.get('FromPort', 'All')
    to_port = rule.get('ToPort', 'All')

    # 포트 범위 설정
    if from_port == to_port:
        port_range = str(from_port)
    elif from_port is None and to_port is None:
        port_range = 'All'
    else:
        port_range = f"{from_port}-{to_port}"

    # IP 범위 분석
    ip_ranges = []
    for ip_range in rule.get('IpRanges', []):
        ip_ranges.append(ip_range.get('CidrIp', 'N/A'))

    for ipv6_range in rule.get('Ipv6Ranges', []):
        ip_ranges.append(ipv6_range.get('CidrIpv6', 'N/A'))

    # 참조된 보안 그룹
    referenced_groups = []
    for group_pair in rule.get('UserIdGroupPairs', []):
        referenced_groups.append(group_pair.get('GroupId', 'N/A'))

    # 위험도 평가
    risk_level = assess_rule_risk(protocol, from_port, to_port, ip_ranges, direction)

    return {
        'protocol': protocol,
        'port_range': port_range,
        'ip_ranges': ip_ranges,
        'referenced_groups': referenced_groups,
        'risk_level': risk_level,
        'direction': direction
    }


def assess_rule_risk(protocol, from_port, to_port, ip_ranges, direction):
    """규칙 위험도 평가"""
    # 0.0.0.0/0 (모든 IP) 허용 체크
    open_to_internet = '0.0.0.0/0' in ip_ranges or '::/0' in ip_ranges

    if not open_to_internet:
        return 'low'

    # 인바운드 규칙의 고위험 포트
    high_risk_inbound_ports = [22, 3389, 23, 21, 135, 445, 1433, 3306, 5432, 6379, 27017]

    # 프로토콜이 -1이면 모든 프로토콜 허용
    if protocol == '-1':
        return 'high'

    # 인바운드 규칙 위험도 평가
    if direction == 'inbound':
        # 모든 포트 허용
        if from_port is None or (from_port == 0 and to_port == 65535):
            return 'high'

        # 고위험 포트 체크
        if from_port in high_risk_inbound_ports or to_port in high_risk_inbound_ports:
            return 'high'

        # 넓은 포트 범위
        if from_port and to_port and (to_port - from_port) > 100:
            return 'medium'

    # 아웃바운드 모든 허용은 중위험
    elif direction == 'outbound':
        if protocol == '-1' or (from_port is None and to_port is None):
            return 'medium'

    return 'low'


def analyze_key_pairs(ec2):
    """키 페어 분석"""
    try:
        response = ec2.describe_key_pairs()
        return [{'name': kp['KeyName'], 'fingerprint': kp.get('KeyFingerprint', 'N/A')}
                for kp in response['KeyPairs']]
    except Exception as e:
        return [{"error": str(e)}]


def analyze_ebs_volumes(ec2):
    """EBS 볼륨 분석"""
    volumes = []
    unencrypted_volumes = []

    try:
        response = ec2.describe_volumes()
        for volume in response['Volumes']:
            vol_info = {
                'id': volume['VolumeId'],
                'size': volume['Size'],
                'type': volume['VolumeType'],
                'state': volume['State'],
                'encrypted': volume.get('Encrypted', False),
                'attachments': [att['InstanceId'] for att in volume.get('Attachments', [])]
            }
            volumes.append(vol_info)

            if not vol_info['encrypted']:
                unencrypted_volumes.append(vol_info)

    except Exception as e:
        return [{"error": str(e)}], []

    return volumes, unencrypted_volumes


def generate_report(session, access_key, secret_key, region):
    """EC2 보안 분석 보고서 생성"""
    ec2 = session.client('ec2')

    report = "# EC2 보안 분석 보고서\n\n"
    report += f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # 계정 정보
    account_info = get_account_info(session)
    report += "## 계정 정보\n\n"
    if "error" in account_info:
        report += f"계정 정보 조회 실패: {account_info['error']}\n\n"
    else:
        report += f"- 계정 ID: {account_info['Account']}\n"
        report += f"- 리전: {region}\n\n"

    # 1. EC2 인스턴스 분석
    report += "## 1. EC2 인스턴스\n\n"
    instances = analyze_ec2_instances(ec2)

    if any("error" in inst for inst in instances if isinstance(inst, dict)):
        report += f"EC2 인스턴스 조회 실패: {instances[0]['error']}\n\n"
    elif instances:
        report += f"총 {len(instances)}개의 인스턴스가 발견되었습니다.\n\n"
        report += "| 인스턴스 ID | 타입 | 상태 | 퍼블릭 IP | 프라이빗 IP | 키 페어 |\n"
        report += "|------------|------|------|-----------|-------------|----------|\n"
        for inst in instances:
            report += f"| {inst['id']} | {inst['type']} | {inst['state']} | {inst['public_ip']} | {inst['private_ip']} | {inst['key_name']} |\n"
        report += "\n"
    else:
        report += "실행 중인 EC2 인스턴스가 없습니다.\n\n"

    # 2. 보안 그룹 분석
    report += "## 2. 보안 그룹 분석\n\n"
    security_groups, high_risk_groups = analyze_security_groups(ec2)

    if any("error" in sg for sg in security_groups if isinstance(sg, dict)):
        report += f"보안 그룹 조회 실패: {security_groups[0]['error']}\n\n"
    else:
        report += f"총 {len(security_groups)}개의 보안 그룹이 발견되었습니다.\n\n"

        if high_risk_groups:
            report += "### 고위험 보안 그룹\n\n"
            report += "| 보안 그룹 ID | 이름 | VPC ID | 위험 요소 |\n"
            report += "|-------------|------|--------|----------|\n"

            for sg in high_risk_groups:
                risk_factors = []
                for rule in sg['inbound_rules']:
                    if rule['risk_level'] == 'high':
                        if '0.0.0.0/0' in rule['ip_ranges']:
                            risk_factors.append(f"인바운드 {rule['port_range']} 포트 전체 오픈")

                risk_factor_str = ', '.join(risk_factors) if risk_factors else '고위험 규칙 존재'
                report += f"| {sg['id']} | {sg['name']} | {sg['vpc_id']} | {risk_factor_str} |\n"
            report += "\n"

        # 상세 보안 그룹 규칙
        report += "### 보안 그룹 상세 규칙\n\n"
        for sg in security_groups:
            if sg['risk_level'] == 'high':
                report += f"#### {sg['name']} ({sg['id']}) - 위험도: 높음\n\n"

                if sg['inbound_rules']:
                    report += "**인바운드 규칙:**\n"
                    for rule in sg['inbound_rules']:
                        ip_ranges_str = ', '.join(rule['ip_ranges']) if rule['ip_ranges'] else 'N/A'
                        report += f"- {rule['protocol']}:{rule['port_range']} <- {ip_ranges_str}\n"
                    report += "\n"

                if sg['outbound_rules']:
                    report += "**아웃바운드 규칙:**\n"
                    for rule in sg['outbound_rules']:
                        ip_ranges_str = ', '.join(rule['ip_ranges']) if rule['ip_ranges'] else 'N/A'
                        report += f"- {rule['protocol']}:{rule['port_range']} -> {ip_ranges_str}\n"
                    report += "\n"

    # 3. EBS 볼륨 분석
    report += "## 3. EBS 볼륨 분석\n\n"
    volumes, unencrypted_volumes = analyze_ebs_volumes(ec2)

    if any("error" in vol for vol in volumes if isinstance(vol, dict)):
        report += f"EBS 볼륨 조회 실패: {volumes[0]['error']}\n\n"
    else:
        report += f"총 {len(volumes)}개의 EBS 볼륨이 발견되었습니다.\n\n"

        if unencrypted_volumes:
            report += "### 암호화되지 않은 볼륨\n\n"
            report += "| 볼륨 ID | 크기(GB) | 타입 | 상태 | 연결된 인스턴스 |\n"
            report += "|---------|----------|------|------|------------------|\n"
            for vol in unencrypted_volumes:
                attachments = ', '.join(vol['attachments']) if vol['attachments'] else 'N/A'
                report += f"| {vol['id']} | {vol['size']} | {vol['type']} | {vol['state']} | {attachments} |\n"
            report += "\n"
        else:
            report += "모든 EBS 볼륨이 암호화되어 있습니다.\n\n"

    # 4. 키 페어 분석
    report += "## 4. 키 페어\n\n"
    key_pairs = analyze_key_pairs(ec2)

    if any("error" in kp for kp in key_pairs if isinstance(kp, dict)):
        report += f"키 페어 조회 실패: {key_pairs[0]['error']}\n\n"
    elif key_pairs:
        report += f"총 {len(key_pairs)}개의 키 페어가 등록되어 있습니다.\n\n"
        report += "| 키 페어 이름 | 지문 |\n"
        report += "|-------------|------|\n"
        for kp in key_pairs:
            report += f"| {kp['name']} | {kp['fingerprint']} |\n"
        report += "\n"
    else:
        report += "등록된 키 페어가 없습니다.\n\n"

    # 5. 전반적인 보안 평가
    report += "## 전반적인 보안 평가\n\n"

    security_issues = []
    if high_risk_groups:
        security_issues.append("고위험 보안 그룹이 발견되었습니다.")
    if unencrypted_volumes:
        security_issues.append("암호화되지 않은 EBS 볼륨이 발견되었습니다.")

    public_instances = [inst for inst in instances if isinstance(inst, dict) and inst.get('public_ip') != 'N/A']
    if public_instances:
        security_issues.append(f"{len(public_instances)}개의 인스턴스가 퍼블릭 IP를 가지고 있습니다.")

    if security_issues:
        report += "### 발견된 보안 문제:\n\n"
        for issue in security_issues:
            report += f"- {issue}\n"
        report += "\n### 권장 조치:\n\n"
        report += "- 0.0.0.0/0으로 열린 보안 그룹 규칙을 필요한 IP 범위로 제한하세요.\n"
        report += "- SSH(22), RDP(3389) 포트는 특정 IP에서만 접근 가능하도록 설정하세요.\n"
        report += "- 모든 EBS 볼륨에 암호화를 적용하세요.\n"
        report += "- 퍼블릭 IP가 필요하지 않은 인스턴스는 프라이빗 서브넷으로 이동하세요.\n"
        report += "- 사용하지 않는 키 페어는 정기적으로 삭제하세요.\n"
    else:
        report += "주요 보안 문제가 발견되지 않았습니다. 다음 모범 사례를 계속 유지하세요:\n\n"
        report += "- 정기적인 보안 그룹 규칙 검토\n"
        report += "- 최소 권한 원칙 적용\n"
        report += "- VPC Flow Logs 활성화\n"
        report += "- AWS Config를 통한 리소스 모니터링\n"

    return report


def save_report(report, filename=None):
    """보고서를 파일로 저장"""
    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f'ec2_security_report_{timestamp}.md'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"보고서가 생성되었습니다: {filename}")


def main():
    parser = argparse.ArgumentParser(description='EC2 보안 분석')
    parser.add_argument('access_key', help='AWS access key')
    parser.add_argument('secret_key', help='AWS secret key')
    parser.add_argument('region', help='AWS region')
    parser.add_argument('-o', '--output', help='출력 파일명')

    args = parser.parse_args()

    # AWS 세션 생성
    session = create_aws_session(args.access_key, args.secret_key, args.region)

    # 보고서 생성
    report = generate_report(session, args.access_key, args.secret_key, args.region)

    # 보고서 저장
    save_report(report, args.output)


if __name__ == "__main__":
    main()