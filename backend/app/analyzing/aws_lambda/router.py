from fastapi import APIRouter, WebSocket
import datetime
import asyncio
import json
import os

router = APIRouter()

@router.websocket("/ws/analyzing/aws/lambda")
async def analyze_aws_lambda_policy(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "[AWS aws_lambda 정책 분석] - WebSocket 연결됨. 분석 요청을 기다립니다..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")

        await websocket.send_text(json.dumps({"type": "log", "message": access_key}))
        await websocket.send_text(json.dumps({"type": "log", "message": secret_key}))
        await websocket.send_text(json.dumps({"type": "log", "message": region}))

        SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "lambda_analyzer.py")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"lambda_analyzer_{timestamp}.md"

        process = await asyncio.create_subprocess_exec(
            "python", SCRIPT_PATH,
            access_key,
            secret_key,
            region,
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


