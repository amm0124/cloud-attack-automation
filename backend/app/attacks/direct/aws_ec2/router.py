from fastapi import APIRouter, WebSocket, Query
import datetime
import asyncio
import json
import os

router = APIRouter()


# ssh brute force attack
@router.websocket("/ws/attacks/direct/ssh-brute-force")
async def ssh_brute_force_attack(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 시작..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        target_ip = data.get("target_ip")

        script_path = os.path.join(os.path.dirname(__file__), "ssh_brute_force.py")
        user_file_path = os.path.join(os.path.dirname(__file__), "user.txt")
        password_file_path = os.path.join(os.path.dirname(__file__), "password.txt")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"ssh_brute_force_{timestamp}.md"

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            target_ip,
            "-u", user_file_path,
            "-p", password_file_path,
            "-o", output_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))

        await process.wait()

        url = f"/download/{output_file}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()


# ssh race condition attack
@router.websocket("/ws/attacks/direct/rce")
async def rce_attack(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 시작..."}))
    try :
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        target_ip = data.get("target_ip")
        script_path = os.path.join(os.path.dirname(__file__), "aws_ec2_rce.py")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"aws_ec2_rce_{timestamp}.md"

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--target", target_ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))

        await process.wait()
        url = f"/download/{output_file}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))


    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()

# ssh temp key
@router.websocket("/ws/attacks/direct/ssh-temp-key")
async def ssh_temp_key_attack(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 시작..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        ec2_instance_id = data.get("instance_id")
        keypair_name = data.get("keypair_name")
        script_path = os.path.join(os.path.dirname(__file__), "aws_ec2_temp_key.py")
        output_file = f"{keypair_name}.pem"

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--instance-id", ec2_instance_id,
            "--keypair-name", keypair_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))

        await process.wait()
        url = f"/download/{output_file}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()


# ec2 stop attack
@router.websocket("/ws/attacks/direct/ec2-stop")
async def ec2_stop_attack(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 시작..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        ec2_instance_id = data.get("instance_id")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"ec2_stop_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)
        script_path = os.path.join(os.path.dirname(__file__), "aws_ec2_stop.py")

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--instance-id", ec2_instance_id,
            "--output-file", output_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))

        await process.wait()
        url = f"/download/{output_file_name}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))


    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()

# ec2 remove attack
@router.websocket("/ws/attacks/direct/ec2-remove")
async def ec2_remove_attack(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 공격 시작..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        ec2_instance_id = data.get("instance_id")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"ec2_remove_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)
        script_path = os.path.join(os.path.dirname(__file__), "aws_ec2_remove.py")

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--instance-id", ec2_instance_id,
            "--output-file", output_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))

        await process.wait()
        url = f"/download/{output_file_name}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))


    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()

# @router.websocket("/ws/attacks/direct/dos")
# async def aws_lambda_malicious_code_injection(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 분석 요청을 기다립니다..."}))
#
#     try:
#         init_data = await websocket.receive_text()
#         data = json.loads(init_data)
#
#         target_ip = data.get("target_ip")
#         target_port = data.get("target_port", 8080)
#         SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "aws_ec2_dos.py")
#
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
#         #output_file = f"aws_lambda_injection_{timestamp}.md"
#
#         process = await asyncio.create_subprocess_exec(
#             "python", SCRIPT_PATH,
#             "--target", target_ip,
#             "--port", target_port,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.STDOUT,
#         )
#
#         while True:
#             line = await process.stdout.readline()
#             if not line:
#                 break
#             await websocket.send_text(json.dumps({"type": "log", "message": line.decode().strip()}))
#
#         await process.wait()
#
#         #url = f"/download/{output_file}"
#         #await websocket.send_text(json.dumps({"type": "download_url", "url": url}))
#
#     except Exception as e:
#         await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
#
#     await websocket.close()





