import asyncio
import subprocess
import json
import os

async def run_nmap_scan(target_ip_range: str, output_file: str, websocket=None):
    nmap_path = r"C:\Users\user\Nmap\nmap.exe"
    output_file = os.path.abspath(output_file)

    print(f"[DEBUG] Running nmap: {nmap_path}")
    print(f"[DEBUG] Output file: {output_file}")

    cmd = [
        nmap_path,
        "-p", "8080,80,443",
        "-sV",
        "-oX", output_file,
        target_ip_range
    ]

    def run_cmd():
        # 동기적으로 nmap 실행
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    try:
        result = await asyncio.to_thread(run_cmd)
        print("[DEBUG] Subprocess finished")
    except Exception as e:
        print(f"[ERROR] Failed to run subprocess: {e}")
        raise

    # 표준 출력 로그 WebSocket 전송
    if websocket and result.stdout:
        for line in result.stdout.splitlines():
            try:
                await websocket.send_text(json.dumps({"type": "log", "stream": "stdout", "message": line}))
            except Exception as e:
                print(f"[ERROR] WebSocket send error: {e}")

    # 표준 에러 로그 WebSocket 전송
    if websocket and result.stderr:
        for line in result.stderr.splitlines():
            try:
                await websocket.send_text(json.dumps({"type": "log", "stream": "stderr", "message": line}))
            except Exception as e:
                print(f"[ERROR] WebSocket send error: {e}")

    if result.returncode != 0:
        error_msg = result.stderr.strip()
        print(f"[ERROR] nmap error: {error_msg}")
        raise Exception(f"nmap exited with code {result.returncode}: {error_msg}")

    print("[DEBUG] nmap scan finished successfully")
    return output_file
