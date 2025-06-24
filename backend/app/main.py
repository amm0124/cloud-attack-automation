from fastapi import FastAPI
from fastapi import APIRouter
from collecting.github.router import router as github_collector_router
from collecting.nmap.router import router as nmap_collector_router
from analyzing.iam.router import router as iam_analyzer_router
from analyzing.ec2.router import router as ec2_analyzer_router
from analyzing.s3.router import router as s3_analyzer_router
from analyzing.aws_lambda.router import router as lambda_analyzer_router
from attacks.direct.router import router as ssh_brute_force_direct_attack_router
from attacks.direct.aws_lambda.router import router as aws_lambda_injection_routers
from attacks.direct.aws_ec2.router import router as aws_ec2_direct_attack_router
from analyzing.jenkins.router import router as jenkins_analyzer_router
from attacks.indirect.router import router as indirect_attack_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse
from fastapi import HTTPException
import os
app = FastAPI()
app.include_router(github_collector_router)
app.include_router(nmap_collector_router)
app.include_router(iam_analyzer_router)
app.include_router(ec2_analyzer_router)
app.include_router(s3_analyzer_router)
app.include_router(lambda_analyzer_router)
app.include_router(ssh_brute_force_direct_attack_router)
app.include_router(aws_lambda_injection_routers)
app.include_router(aws_ec2_direct_attack_router)
app.include_router(jenkins_analyzer_router)
app.include_router(indirect_attack_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용으로 모든 origin 허용 (보안상 배포 시에는 도메인 지정 필요)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REPORTS_DIR = "/Users/geonho/workspace/cloud-attack-automation/backend/app" # 보고서 저장 경로
REPORTS_DIR = "/Users/user/cloud-attack-automation/cloud-attack-automation/backend/"

router = APIRouter()

@router.get("/download/{filename}", summary="보고서 작성 후 다운로드 및 삭제")
async def download_report(filename: str):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(REPORTS_DIR, safe_filename)
    print("file_path", file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")

    def file_streamer(path):
        with open(path, mode="rb") as file:
            yield from file
        try:
            os.remove(path)
            print(f"다운로드 후 성공적으로 삭제됨: {path}")
        except Exception as e:
            print(f"삭제 실패: {e}")

    return StreamingResponse(
        file_streamer(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
    )

app.include_router(router)
