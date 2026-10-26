# ☸️ CKA (Certified Kubernetes Administrator) 실전 학습 상황판 (`CKA_PROGRESS.md`)

> **문서 목적 (Living Tracker)**:
> FastAPI 트랙(Step 1~8) 완주 후, **로컬 PC(Windows 32GB)**에서 먼저 CKA 시험 5대 도메인을 100% 실습·체득하기 위한 진행 대시보드 및 **실전 트러블슈팅 오답노트**입니다.
> 각 미션 가이드는 **`docs/missions/cka/`** 폴더 아래에 개별 문서로 생성됩니다.
> **진행 원칙**: **로컬 클러스터(Docker Desktop K8s / kind)에서 100% 먼저 정복 → 이후 라즈베리파이 + 서브 노트북 물리 클러스터로 확장!**

---

## 📊 로컬 CKA 실전 커리큘럼 (CKA Exam 100% 매핑)

| 단계 | CKA 시험 도메인 (배점) | 핵심 실습 내용 | 미션 가이드 문서 | 상태 |
| :--- | :--- | :--- | :--- | :---: |
| **CKA-01** | **Cluster & Pod 기초 (25%)** | `Dockerfile` 빌드, 로컬 K8s(`kubectl`) 연결, `--dry-run=client -o yaml`로 첫 파드 배포 | [`step-01-docker-and-local-k8s.md`](./missions/cka/step-01-docker-and-local-k8s.md) | ✅ **완료** |
| **CKA-02** | **Storage & Config (10%)** | `Namespace`, `ConfigMap`, `Secret` 주입 및 `PV` / `PVC` 공유 볼륨 바인딩 (`k8s/02-storage-config/`) | [`step-02-storage-and-config.md`](./missions/cka/step-02-storage-and-config.md) | 🔄 **진행 중** |
| **CKA-03** | **Workloads & Sidecar (15%)** | `Deployment`, Liveness(`/healthz`)/Readiness(`/readyz`) Probe, **Multi-Container Sidecar (`emptyDir`)**, Rollout/Undo | *(대기)* | ⏳ 대기 |
| **CKA-04** | **RBAC, Jobs & Scheduling (25%)** | `ServiceAccount`, `Role`, `RoleBinding` (`auth can-i` 검증), `Job`/`CronJob`, `NodeAffinity` & `Taint` | *(대기)* | ⏳ 대기 |
| **CKA-05** | **Services & NetworkPolicy (20%)** | `ClusterIP`, `NodePort`, `Ingress`, **`NetworkPolicy`**로 파드 간 트래픽 격리 | *(대기)* | ⏳ 대기 |
| **CKA-06** | **Troubleshooting (30% — 최고 배점)** | 일부러 고장 낸 시나리오(Break & Fix)를 `describe`, `logs`, `events`로 원인 찾아 복구하기 | *(대기)* | ⏳ 대기 |
| **CKA-07** | **물리 홈랩 실전 (심화 25%)** | 라즈베리파이 `kubeadm init`, `etcdctl snapshot save/restore`, 노트북 워커 `cordon`/`drain` | *(후반부)* | ⏳ 대기 |

---

## 📌 현재 활성 미션 요약
* **현재 스텝**: **CKA-02 — `Namespace`, `ConfigMap`, `Secret` 주입 및 `PV`/`PVC` 볼륨 마운트**
* **가이드 위치**: [`docs/missions/cka/step-02-storage-and-config.md`](./missions/cka/step-02-storage-and-config.md)
* **체크 대상**:
  1. `kube-pipeline` 네임스페이스 생성 (`k8s/02-storage-config/01-namespace.yaml`)
  2. `pipeline-config` (`ConfigMap`), `pipeline-secret` (`Secret`) 명령형 생성 및 배포 (`02-configmap.yaml`, `03-secret.yaml`)
  3. `pipeline-pv` (`PV`) 및 `pipeline-pvc` (`PVC`) 생성 및 `Bound` 상태 확인 (`04-pv-pvc.yaml`)
  4. `pipeline-storage-pod`에 `envFrom` 및 `volumeMounts` 장착 후 `Running` 및 환경변수(`NODE_NAME=k8s-local-cluster`) 주입 확인 (`05-pod-storage.yaml`)

---

## 🛠️ 실전 트러블슈팅 & 오답노트 기록 (Troubleshooting Log)

실습 중 직접 겪고 해결한 문제들입니다 (CKA 시험의 30%를 차지하는 트러블슈팅 핵심 자산!):

### 🔧 [Troubleshooting #1] `docker build` 시 `"/app": not found` (`COPY requirements.txt .` 실패)
* **증상**: `docker build -t kube-pipeline-api:v1 .` 실행 시 `transferring context: 2B`만 전송되고 `COPY requirements.txt .` 및 `COPY app ./app` 단계에서 파일을 찾지 못해 실패.
* **원인**: 루트 디렉토리에 `Dockerfile` 파일이 아니라 `Dockerfile\`이라는 **폴더**가 생성되고 그 안에 `Dockerfile\Dockerfile`이 들어가 있어서 빌드 컨텍스트 경로가 어긋남.
* **해결**: `Dockerfile` 파일을 프로젝트 루트(`requirements.txt`, `app/`과 동일한 위치)로 이동시켜 해결.
* **교훈**: `docker build ... .`의 마지막 마침표(`.`)는 **"현재 폴더(Build Context)의 파일들을 도커 데몬에 보내라"**는 뜻이므로, 항상 `COPY`할 대상 파일들이 있는 루트 경로에 `Dockerfile`을 두고 실행해야 한다.

### 🔧 [Troubleshooting #2] 파드 생성 후 `STATUS: ErrImageNeverPull` 발생 (CKA 핵심!)
* **증상**: `docker build`로 `kube-pipeline-api:v1` 이미지를 분명히 만들었으나(`docker images`에서 확인됨), `kubectl apply`로 띄운 `pipeline-pod`가 `0/1 ErrImageNeverPull` 상태에서 멈춤.
* **진단 과정**:
  1. `kubectl get nodes -o wide`로 노드의 컨테이너 런타임 확인 ➡️ 노드가 `desktop-control-plane` (런타임: `containerd://2.3.1`)임을 확인.
  2. **원인 규명**: 호스트 PC에서 `docker build`한 이미지는 호스트의 **Docker 데몬 스토리지**에 저장되지만, 쿠버네티스 노드(`desktop-control-plane`)는 내부적으로 격리된 **`containerd` (`k8s.io` 네임스페이스)** 컨테이너 런타임을 사용한다. 따라서 노드의 `containerd` 안에는 이미지가 없었고, `imagePullPolicy: Never`(외부 레지스트리 Pull 금지) 설정 때문에 `ErrImageNeverPull`이 발생함.
* **해결 명령어**:
  도커 이미지를 `.tar`로 추출하여 쿠버네티스 노드의 `containerd` (`-n k8s.io`)에 직접 import 수행:
  ```powershell
  docker save kube-pipeline-api:v1 -o image.tar
  docker cp image.tar desktop-control-plane:/image.tar
  docker exec desktop-control-plane ctr -n k8s.io images import /image.tar
  Remove-Item image.tar
  ```
  이후 파드 재생성 시 즉시 **`1/1 Running`** 전환 성공!
* **CKA 시험 연계 포인트**: 실제 CKA 시험 클러스터도 모두 도커가 아닌 **`containerd`**를 런타임으로 사용하며, 노드 내부 이미지를 다룰 때는 `crictl images` 또는 `ctr -n k8s.io images ls`를 사용한다!

---

## 📝 CKA 학습 히스토리 (Agent Updated)
* **2026-10-26 (CKA-01 완료)**:
  * `Dockerfile` 작성 및 `kube-pipeline-api:v1` 이미지 빌드 완료.
  * `kubectl run pipeline-pod ... --dry-run=client -o yaml > k8s/01-cluster-setup/first-pod.yaml`로 매니페스트 생성 완료.
  * `desktop-control-plane` (`containerd`) 이미지 import 트러블슈팅 완수 및 `pipeline-pod` `1/1 Running` 검증 완료!
  * CKA-02 가이드([`step-02-storage-and-config.md`](./missions/cka/step-02-storage-and-config.md)) 오픈.
