from fastapi import APIRouter, WebSocket, Query
import datetime
import asyncio
import json
import os

router = APIRouter()

@router.websocket("/ws/attacks/direct/download-lambda")
async def aws_lambda_download(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. lambda 코드를 다운합니다..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        function_name = data.get("function_name")

        script_path = os.path.join(os.path.dirname(__file__), "aws_lambda_download.py")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"aws_lambda_download_{timestamp}.zip"
        output_file = os.path.join(output_dir, output_file_name)

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--function-name", function_name,
            "--output", output_file,
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


@router.websocket("/ws/attacks/direct/lambda-injection")
async def aws_lambda_injection(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. lambda에 악성 코드를 삽입합니다..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        function_name = data.get("function_name")

        script_path = os.path.join(os.path.dirname(__file__), "aws_lambda_injection.py")
        malicious_code_path = os.path.join(os.path.dirname(__file__), "lambda_malicious_code.zip")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"ssh_brute_force_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--function-name", function_name,
            "--file", malicious_code_path,
            "--output", output_file,
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






@router.websocket("/ws/attacks/direct/stop-lambda")
async def aws_lambda_remove(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. lambda를 중지합니다 ..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        function_name = data.get("function_name")

        script_path = os.path.join(os.path.dirname(__file__), "aws_lambda_stop.py")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"aws_lambda_stop_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)


        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--function-name", function_name,
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

        url = f"/download/{output_file}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()



@router.websocket("/ws/attacks/direct/remove-lambda")
async def aws_lambda_remove(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 분석 요청을 기다립니다..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        function_name = data.get("function_name")

        script_path = os.path.join(os.path.dirname(__file__), "aws_lambda_remove.py")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"aws_lambda_remove_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)


        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--function-name", function_name,
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

        url = f"/download/{output_file}"
        await websocket.send_text(json.dumps({"type": "download_url", "url": url}))

    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    await websocket.close()









