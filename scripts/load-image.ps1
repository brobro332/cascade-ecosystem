# ==============================================================================
# 로컬 Docker 이미지를 Docker Desktop K8s 노드(desktop-control-plane)에 적재하는 헬퍼
# 사용법: .\scripts\load-image.ps1 [이미지이름:태그]
# (참고: 이 스크립트는 로컬 PC 실습 편의용이며, CKA 시험 범위가 아닙니다!)
# ==============================================================================
param(
    [string]$ImageName = "kube-pipeline-api:v1"
)

Write-Host "[1/3] Saving Docker image '$ImageName'..." -ForegroundColor Cyan
docker save $ImageName -o image.tar

Write-Host "[2/3] Copying & importing into 'desktop-control-plane' containerd..." -ForegroundColor Cyan
docker cp image.tar desktop-control-plane:/image.tar
docker exec desktop-control-plane ctr -n k8s.io images import /image.tar

Write-Host "[3/3] Cleaning up temporary file..." -ForegroundColor Cyan
Remove-Item -Force image.tar

Write-Host "✅ Done! '$ImageName' is now ready in local Kubernetes!" -ForegroundColor Green
