# from fastapi import APIRouter, WebSocket, Query
# import datetime
# import asyncio
# import json
# import os
#
# router = APIRouter()
#
# @router.websocket("/ws/attacks/direct/lambda-injection")
# async def aws_lambda_malicious_code_injection(websocket: WebSocket):
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
#         function_name = data.get("function_name")
#
#         SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "aws_lambda_injection.py")
#         malicious_code_path = os.path.join(os.path.dirname(__file__), "lambda_malicious_code.zip")
#
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
#         output_file = f"aws_lambda_injection_{timestamp}.md"
#
#         process = await asyncio.create_subprocess_exec(
#             "python", SCRIPT_PATH,
#             "--access-key", access_key,
#             "--secret-key", secret_key,
#             "--region", region,
#             "--function-name", function_name,
#             "--file", malicious_code_path,
#             "--output", output_file,
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
#         url = f"/download/{output_file}"
#         await websocket.send_text(json.dumps({"type": "download_url", "url": url}))
#
#     except Exception as e:
#         await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
#
#     await websocket.close()
#
#
#
#
#
# @router.websocket("/ws/attacks/direct/ssh-brute-force")
# async def ssh_brute_force_attack(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket 연결됨. 분석 요청을 기다립니다..."}))
#
#     try:
#         init_data = await websocket.receive_text()
#         data = json.loads(init_data)
#         target_ip = data.get("target_ip")
#
#         SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "ssh_brute_force.py")
#         USER_FILE_PATH = os.path.join(os.path.dirname(__file__), "user.txt")
#         PASSWORD_FILE_PATH = os.path.join(os.path.dirname(__file__), "password.txt")
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
#         output_file = f"ssh_brute_force_{timestamp}.md"
#
#         process = await asyncio.create_subprocess_exec(
#             "python", SCRIPT_PATH,
#             target_ip,
#             "-u", USER_FILE_PATH,
#             "-p", PASSWORD_FILE_PATH,
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
#         url = f"/download/{output_file}"
#         await websocket.send_text(json.dumps({"type": "download_url", "url": url}))
#
#     except Exception as e:
#         await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
#
#     await websocket.close()
#
#
#
#
