from fastapi import APIRouter, WebSocket, Query
import datetime
import asyncio
import json
import os

router = APIRouter()

@router.websocket("/ws/collecting/github")
async def collect_github_credentials(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 분석 요청을 기다립니다..."}))

    try:
        init_data = await websocket.receive_text()
        data = json.loads(init_data)
        github_url = data.get("github_url")

        SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "gitleaks_trufflehog.py")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = f"collect_github_credentials_{timestamp}.md"

        process = await asyncio.create_subprocess_exec(
            "python", SCRIPT_PATH,
            github_url,
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