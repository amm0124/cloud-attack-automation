# from fastapi import APIRouter, WebSocket, Query
# import datetime
# import asyncio
# import json
# import os
#
# router = APIRouter()
#
# @router.websocket("/ws/attacks/direct/temporary-key")
# async def ssh_brute_force_attack(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 분석 요청을 기다립니다..."}))
#
#     try:
#         init_data = await websocket.receive_text()
#         data = json.loads(init_data)
#
#         access_key = data.get("access_key")
#         secret_key = data.get("secret_key")
#         region = data.get("region")
#         instance_id = data.get("instance_id")
#
#         print(f"Received data: {data}")
#
#
#
#         SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "ssh_temp_key.py")
#
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
#         output_file = f"ssh_temp_key_{timestamp}"
#
#         process = await asyncio.create_subprocess_exec(
#             "python", SCRIPT_PATH,
#             "-a", access_key,
#             "-s", secret_key,
#             "-r", region,
#             "-i", instance_id,
#             "-o", output_file,
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
#         url = f"/download/{output_file}.pem"
#         await websocket.send_text(json.dumps({"type": "download_url", "url": url}))
#
#     except Exception as e:
#         await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
#
#     await websocket.close()
#
#
