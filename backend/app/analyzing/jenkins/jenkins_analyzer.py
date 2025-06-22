import httpx
import re

async def fetch_jenkins_version(jenkins_url: str) -> str:
    """
    Jenkins 서버에서 버전 정보를 가져온다.
    Jenkins는 보통 HTTP 응답 헤더 'X-Jenkins'에 버전 정보를 담고 있다.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(jenkins_url)
        version = response.headers.get("X-Jenkins", "")
        return version


def is_version_vulnerable(version_str: str) -> bool:
    """
    Jenkins 버전 문자열을 파싱해 취약 여부 판단.
    2.440 이하 버전을 취약으로 가정.
    """
    pattern = r"(\d+)\.(\d+)"
    match = re.match(pattern, version_str)
    if not match:
        return False

    major, minor = int(match.group(1)), int(match.group(2))
    if major < 2 or (major == 2 and minor <= 440):
        return True

    return False
