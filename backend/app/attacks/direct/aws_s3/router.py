from fastapi import APIRouter, WebSocket, Query
import datetime
import asyncio
import json
import os

router = APIRouter()

@router.websocket("/ws/attacks/direct/remove-s3")
async def aws_lambda_download(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. S3 Bucket을 삭제합니다 ..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)

        access_key = data.get("access_key")
        secret_key = data.get("secret_key")
        region = data.get("region")
        bucket_name = data.get("bucket_name")

        script_path = os.path.join(os.path.dirname(__file__), "aws_s3_remove.py")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "report")
        output_file_name = f"aws_s3_remove_{timestamp}.md"
        output_file = os.path.join(output_dir, output_file_name)

        process = await asyncio.create_subprocess_exec(
            "python", script_path,
            "--access-key", access_key,
            "--secret-key", secret_key,
            "--region", region,
            "--bucket-name", bucket_name,
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

