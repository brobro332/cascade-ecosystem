# ☸️ CKA (Certified Kubernetes Administrator) 실전 학습 상황판 & 해설집 (`CKA_PROGRESS.md`)

> **문서 목적 (Living Tracker & Study Book)**:
> 이 문서는 단순 진도표가 아니라, **각 미션에서 우리가 도대체 무엇을 왜 만들었는지 쉬운 비유로 복습하는 '미션별 해설집'**이자 **'실전 트러블슈팅 오답노트'**입니다.
> 각 미션 실습 가이드는 **`docs/missions/cka/`** 폴더 아래에 있습니다.

---

## 📊 로컬 CKA 실전 커리큘럼 (CKA Exam 100% 매핑)

| 단계 | CKA 시험 도메인 (배점) | 핵심 실습 내용 | 미션 가이드 문서 | 상태 |
| :--- | :--- | :--- | :--- | :---: |
| **CKA-01** | **Cluster & Pod 기초 (25%)** | `Dockerfile` 빌드, 로컬 K8s(`kubectl`) 연결, `--dry-run=client -o yaml`로 첫 파드 배포 | [`step-01-docker-and-local-k8s.md`](./missions/cka/step-01-docker-and-local-k8s.md) | ✅ **완료** |
| **CKA-02** | **Storage & Config (10%)** | `Namespace`, `ConfigMap`, `Secret` 주입 및 `PV` / `PVC` 공유 볼륨 바인딩 (`k8s/02-storage-config/`) | [`step-02-storage-and-config.md`](./missions/cka/step-02-storage-and-config.md) | ✅ **완료** |
| **CKA-03** | **Workloads & Sidecar (15%)** | `Deployment`, Liveness(`/healthz`)/Readiness(`/readyz`) Probe, **Multi-Container Sidecar (`emptyDir`)** | [`step-03-workloads-and-sidecar.md`](./missions/cka/step-03-workloads-and-sidecar.md) | 🔄 **진행 중** |
| **CKA-04** | **RBAC, Jobs & Scheduling (25%)** | `ServiceAccount`, `Role`, `RoleBinding` (`auth can-i` 검증), `Job`/`CronJob`, `NodeAffinity` & `Taint` | *(대기)* | ⏳ 대기 |
| **CKA-05** | **Services & NetworkPolicy (20%)** | `ClusterIP`, `NodePort`, `Ingress`, **`NetworkPolicy`**로 파드 간 트래픽 격리 | *(대기)* | ⏳ 대기 |
| **CKA-06** | **Troubleshooting (30% — 최고 배점)** | 일부러 고장 낸 시나리오(Break & Fix)를 `describe`, `logs`, `events`로 원인 찾아 복구하기 | *(대기)* | ⏳ 대기 |
| **CKA-07** | **물리 홈랩 실전 (심화 25%)** | 라즈베리파이 `kubeadm init`, `etcdctl snapshot save/restore`, 노트북 워커 `cordon`/`drain` | *(후반부)* | ⏳ 대기 |

---

## 📚 미션별 완료 해설집 (내가 한 작업 완벽 복습 노트)

### 📘 [CKA-01 해설] 내 FastAPI 앱을 도커로 포장하고 첫 파드(`Pod`) 띄우기
* **전체 줄거리 요약**:
  쿠버네티스는 파이썬 파일(`.py`)을 직접 실행할 줄 모르고 오직 **컨테이너 이미지(밀키트 상자)**만 실행할 수 있습니다. 그래서 우리가 만든 FastAPI 앱을 `Dockerfile`로 포장해 첫 번째 원룸 방(`Pod`)에 입주시킨 미션입니다.
* **내가 만든 파일별 해설**:
  1. **[`Dockerfile`](../Dockerfile)**:
     * 파이썬 3.12(`FROM python:3.12-slim`)와 패키지(`requirements.txt`), 우리 코드(`app/`)를 한 상자에 넣어 `kube-pipeline-api:v1`이라는 이름의 밀키트로 포장한 레시피입니다.
     * `--host 0.0.0.0`을 준 이유: 기본값(`127.0.0.1`)으로 띄우면 파드 방문이 잠겨서 바깥에서 접속할 수 없기 때문에 모든 문을 열어준 것입니다.
  2. **[`k8s/01-cluster-setup/first-pod.yaml`](../k8s/01-cluster-setup/first-pod.yaml)**:
     * 손으로 타이핑하지 않고 `kubectl run pipeline-pod --image=... --dry-run=client -o yaml` 명령어로 자동 생성한 파드 주문서입니다.
     * `imagePullPolicy: Never`: "인터넷(Docker Hub)에서 이미지 찾지 말고 내 컴퓨터에 있는 이미지를 써라!"라는 뜻입니다.
* **핵심 명령어 정리**:
  * 파드 올리기: `kubectl apply -f 파일.yaml`
  * 파드 확인하기: `kubectl get pods -o wide`
  * 파드 1초 만에 강제 삭제하기(CKA 꿀팁): `kubectl delete pod 파드이름 --force --grace-period=0`

---

### 📗 [CKA-02 해설] 원룸(`Pod`)에 살림살이 들여놓기 (`Namespace`, `ConfigMap`, `Secret`, `PV`, `PVC`)
* **전체 줄거리 요약 ('원룸 자취방' 비유)**:
  미션 1에서 빈 원룸(`Pod`)에 몸만 들어갔더니 두 가지 문제가 있었습니다:
  1. 설정값을 바꿀 때마다 파이썬 코드를 다시 짜야 함 ➡️ **`ConfigMap`(설정 메모장)**과 **`Secret`(비밀번호 금고)**으로 해결!
  2. 파드는 '모래성'이라 재시작되면 파드 안에 올린 파일이 100% 증발함 ➡️ **`PV`(외장하드 실물)**와 **`PVC`(외장하드 대여 티켓)**로 해결!
* **내가 만든 5개 파일 완벽 해부 (`k8s/02-storage-config/`)**:
  1. **`01-namespace.yaml` (`Namespace: kube-pipeline`) — 전용 층(구역) 나누기**:
     * 기본 구역(`default`)에 다른 파드들과 섞이지 않도록 `kube-pipeline`이라는 우리 전용 구역을 만들었습니다. (앞으로 모든 명령어에 `-n kube-pipeline`을 붙이는 이유!)
  2. **`02-configmap.yaml` (`ConfigMap: pipeline-config`) — 설정 포스트잇 메모장**:
     * 파이썬 코드를 안 건드리고 바깥에서 `NODE_NAME=k8s-local-cluster`, `UPLOAD_DIR=/app/storage/uploads` 환경변수를 주입하기 위한 메모장입니다.
  3. **`03-secret.yaml` (`Secret: pipeline-secret`) — 비밀번호 금고**:
     * `API_SECRET_KEY`처럼 민감한 정보를 Base64로 인코딩해서 보관하는 금고입니다.
  4. **`04-pv-pvc.yaml` (`PV` & `PVC`) — 파드가 죽어도 파일이 안 날아가는 외장하드 대여 시스템!**:
     * **왜 `PV`랑 `PVC` 두 개로 나눴나요?**
       * **`PV` (PersistentVolume = 외장하드 기계 실물)**: 인프라 관리자가 창고에 준비해 둔 **1Gi짜리 실제 저장 공간**(`pipeline-pv`, 실제 경로 `/tmp/pipeline-data`).
       * **`PVC` (PersistentVolumeClaim = 외장하드 대여 티켓)**: 개발자(파드)가 *"저 1Gi짜리 외장하드 하나 빌려주세요!"* 하고 제출하는 **대여 신청서**(`pipeline-pvc`).
       * **`Bound` 상태**: 창고의 1Gi 외장하드(`PV`)와 내 대여 신청서(`PVC`)가 짝이 맞아서 **계약 성사(연결 완료)**된 상태!
  5. **`05-pod-storage.yaml` (`Pod: pipeline-storage-pod`) — 설정과 외장하드를 파드에 장착!**:
     * `envFrom`: ConfigMap 메모장과 Secret 금고의 내용물을 파드 환경변수로 한 방에 쏟아부음 (덕분에 우리 FastAPI `config.py`의 `node_name`이 자동으로 `"k8s-local-cluster"`로 바뀜!).
     * `volumes` & `volumeMounts`: 대여 티켓(`claimName: pipeline-pvc`)으로 빌려온 외장하드를 파드 안의 `/app/storage/uploads` 폴더에 USB처럼 꽂아줌!
* **💬 미션 2 핵심 Q&A 복습**:
  * **Q. `kubectl create configmap ... --from-literal=...` 같은 긴 명령어를 다 외워서 치나요?**
  * **A. 절대 외우지 않습니다!** 터미널에 **`kubectl create configmap -h`** (또는 `kubectl create secret generic -h`)만 치면 맨 위에 복사해서 쓸 수 있는 정답 예제가 그대로 나옵니다!

---

## 🛠️ 실전 트러블슈팅 & 오답노트 기록 (Troubleshooting Log)

### 🔧 [Troubleshooting #1] `docker build` 시 `"/app": not found` (`COPY requirements.txt .` 실패)
* **원인**: 루트 디렉토리에 `Dockerfile` 파일이 아니라 `Dockerfile\` 폴더가 생성되어 빌드 컨텍스트 경로가 어긋남.
* **해결**: `Dockerfile` 파일을 프로젝트 루트로 이동시켜 해결.

### 🔧 [Troubleshooting #2] 파드 생성 후 `STATUS: ErrImageNeverPull` 발생
* **원인**: 호스트 PC에서 `docker build`한 이미지는 Docker 데몬에 저장되지만, 쿠버네티스 노드(`desktop-control-plane`)는 격리된 `containerd` (`k8s.io` 네임스페이스)를 사용함.
* **해결**: 로컬 편의 스크립트 [`scripts/load-image.ps1`](../scripts/load-image.ps1)을 생성하여 `.\scripts\load-image.ps1` 한 줄로 이미지를 노드에 적재하도록 자동화 완료 (CKA 시험 범위 아님, 로컬 실습 전용).

### 🔧 [Troubleshooting #3] `Get "http://localhost:8080/api": dial tcp [::1]:8080: connectex: No connection could be made`
* **원인**: PC 재부팅 후 Docker Desktop 내부 Kubernetes가 중지(Stopped) 상태일 때 `~/.kube/config`에서 Context가 비활성화되어(`kubectl config get-contexts`가 비어 있음) `kubectl`이 기본값인 `localhost:8080`으로 접속을 시도함.
* **해결**: Docker Desktop 실행 및 Kubernetes 클러스터 기동 완료 확인 후 정상 복구.
