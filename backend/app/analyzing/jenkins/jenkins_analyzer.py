import os
import httpx
import json
import re

async def fetch_jenkins_version(jenkins_url: str, websocket=None) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(jenkins_url)
            version = response.headers.get("X-Jenkins", "")
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "message": f"founded Jenkins version: {version}"
                }))
            return version
    except Exception as e:
        if websocket:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"fetch failed: {str(e)}"
            }))
        raise



def is_version_vulnerable(version_str: str) -> bool:
    pattern = r"(\d+)\.(\d+)"
    match = re.match(pattern, version_str)
    if not match:
        return False

    major, minor = int(match.group(1)), int(match.group(2))
    return major < 2 or (major == 2 and minor <= 440)
