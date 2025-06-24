from fastapi import APIRouter, WebSocket
import json
import datetime
from app.collecting.nmap.nmap_scan import run_nmap_scan

router = APIRouter()

@router.websocket("/ws/collecting/nmap")
async def collect_nmap_scan(websocket: WebSocket):
    await websocket.accept()
    print("[DEBUG] WebSocket connection accepted")
    await websocket.send_text(json.dumps({"type": "log", "message": "WebSocket connected. nmap scan request receiving..."}))

    try:
        init_data = await websocket.receive_text()
        print(f"[DEBUG] Received data from client: {init_data}")
        data = json.loads(init_data)
        target_ip_range = data.get("target_ip_range")
        if not target_ip_range:
            await websocket.send_text(json.dumps({"type": "error", "message": "target_ip_range parameter needed"}))
            print("[ERROR] target_ip_range parameter missing")
            await websocket.close()
            return

        output_file = "nmap_scan.md"

        try:
            await run_nmap_scan(target_ip_range, output_file, websocket)
        except Exception as e:
            error_msg = f"nmap scan failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            await websocket.send_text(json.dumps({"type": "error", "message": error_msg}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({"type": "done", "message": f"nmap scan finished, file: {output_file}"}))
        await websocket.send_text(json.dumps({"type": "download_url", "url": f"/download/{output_file}"}))

    except Exception as e:
        error_msg = f"unknown error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        await websocket.send_text(json.dumps({"type": "error", "message": error_msg}))
    finally:
        print("[DEBUG] Closing WebSocket connection")
        await websocket.close()
