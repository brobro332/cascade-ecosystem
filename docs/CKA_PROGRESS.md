# ☸️ CKA (Certified Kubernetes Administrator) 실전 학습 상황판 (`CKA_PROGRESS.md`)

> **문서 목적 (Living Tracker)**:
> FastAPI 트랙(Step 1~8) 완주 후, **로컬 PC(Windows 32GB)**에서 먼저 CKA 시험 5대 도메인을 100% 실습·체득하기 위한 진행 대시보드입니다.
> 각 미션 가이드는 **`docs/missions/cka/`** 폴더 아래에 개별 문서로 생성됩니다.
> **진행 원칙**: **로컬 클러스터(Docker Desktop K8s / kind)에서 100% 먼저 정복 → 이후 라즈베리파이 + 서브 노트북 물리 클러스터로 확장!**

---

## 📊 로컬 CKA 실전 커리큘럼 (CKA Exam 100% 매핑)

| 단계 | CKA 시험 도메인 (배점) | 핵심 실습 내용 | 미션 가이드 문서 | 상태 |
| :--- | :--- | :--- | :--- | :---: |
| **CKA-01** | **Cluster & Pod 기초 (25%)** | `Dockerfile` 빌드, 로컬 K8s(`kubectl`) 연결, `--dry-run=client -o yaml`로 첫 파드 배포 | [`step-01-docker-and-local-k8s.md`](./missions/cka/step-01-docker-and-local-k8s.md) | 🔄 **진행 중** |
| **CKA-02** | **Storage & Config (10%)** | `Namespace`, `ConfigMap`, `Secret` 주입 및 `PV` / `PVC` 공유 볼륨 바인딩 (`k8s/02-storage-config/`) | *(대기)* | ⏳ 대기 |
| **CKA-03** | **Workloads & Sidecar (15%)** | `Deployment`, Liveness(`/healthz`)/Readiness(`/readyz`) Probe, **Multi-Container Sidecar (`emptyDir`)**, Rollout/Undo | *(대기)* | ⏳ 대기 |
| **CKA-04** | **RBAC, Jobs & Scheduling (25%)** | `ServiceAccount`, `Role`, `RoleBinding` (`auth can-i` 검증), `Job`/`CronJob`, `NodeAffinity` & `Taint` | *(대기)* | ⏳ 대기 |
| **CKA-05** | **Services & NetworkPolicy (20%)** | `ClusterIP`, `NodePort`, `Ingress`, **`NetworkPolicy`**로 파드 간 트래픽 격리 | *(대기)* | ⏳ 대기 |
| **CKA-06** | **Troubleshooting (30% — 최고 배점)** | 일부러 고장 낸 시나리오(Break & Fix)를 `describe`, `logs`, `events`로 원인 찾아 복구하기 | *(대기)* | ⏳ 대기 |
| **CKA-07** | **물리 홈랩 실전 (심화 25%)** | 라즈베리파이 `kubeadm init`, `etcdctl snapshot save/restore`, 노트북 워커 `cordon`/`drain` | *(후반부)* | ⏳ 대기 |

---

## 📌 현재 활성 미션 요약
* **현재 스텝**: **CKA-01 — 내 FastAPI 앱을 컨테이너(`Dockerfile`)로 포장하고 로컬 쿠버네티스에 첫 파드 띄우기!**
* **가이드 위치**: [`docs/missions/cka/step-01-docker-and-local-k8s.md`](./missions/cka/step-01-docker-and-local-k8s.md)
* **체크 대상**:
  1. 로컬 `docker` 및 `kubectl get nodes` (`Ready`) 동작 확인
  2. 루트 경로 `Dockerfile` 작성 및 `kube-pipeline-api:v1` 이미지 빌드
  3. `kubectl run ... --dry-run=client -o yaml` 명령어로 `k8s/01-cluster-setup/first-pod.yaml` 생성 및 파드 `Running` 확인
  4. `kubectl port-forward`로 내 쿠버네티스 파드 안의 FastAPI `/healthz` 호출 확인!

---

## 📝 CKA 학습 히스토리 & 코칭 노트 (Agent Updated)
* **2026-10-25**: FastAPI 트랙(Step 1~8) 완주 완료 후, 로컬 우선(Local-First) CKA 실전 트랙 및 첫 번째 미션([`step-01-docker-and-local-k8s.md`](./missions/cka/step-01-docker-and-local-k8s.md)) 오픈.
