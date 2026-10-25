# 🎯 [CKA Mission 01] 내 FastAPI 앱을 Docker로 포장하고 로컬 쿠버네티스에 첫 파드(`Pod`) 띄우기!

> **난이도**: ★☆☆☆☆ (CKA 입문 — 첫걸음!)  
> **CKA 출제 비중**: Workloads & Cluster Fundamentals (기본기 100% 필수)  
> **작업 대상 파일**: `Dockerfile` (신규), `k8s/01-cluster-setup/first-pod.yaml` (신규)  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. 왜 쿠버네티스에 올리려면 `Dockerfile`부터 만들어야 하나요?
* 지금까지 우리는 내 윈도우 PC에서 파이썬 가상환경(`.venv`)을 켜고 `uvicorn`으로 FastAPI를 실행했습니다.
* 하지만 **쿠버네티스는 `.py` 파이썬 파일을 직접 실행할 줄 모릅니다!**
* 쿠버네티스는 오직 **"파이썬 + 라이브러리(`requirements.txt`) + 내 코드(`app/`)가 한 상자에 통째로 밀봉된 밀키트(Docker 컨테이너 이미지)"**만 받아서 실행할 수 있습니다.
* 그 밀키트를 만드는 포장 설명서가 바로 **`Dockerfile`**입니다!

---

### 💡 2. 파드(`Pod`)란 무엇인가요?
* 쿠버네티스에서 프로그램을 띄우는 **가장 작은 단위(원룸 방 1개)**를 **파드(`Pod`)**라고 부릅니다.
* 보통 **파드(방 1개) 안에 컨테이너(세입자 1명 — 우리 FastAPI 앱)**가 들어가서 살게 됩니다. (나중에는 방 1개에 워커 컨테이너와 로그 수집 보조 컨테이너 2명을 같이 넣는 '사이드카 패턴'도 배웁니다!)

---

### 💡 3. CKA 시험 합격 비결 1순위: **"절대 YAML을 처음부터 손으로 타이핑하지 마라!"**
* CKA 실기 시험은 2시간 동안 15~17문제를 풀어야 합니다. YAML 파일의 들여쓰기(스페이스바)를 처음부터 손으로 치면 시간도 부족하고 오타가 납니다.
* 그래서 시험장에서는 무조건 쿠버네티스 명령어 뒤에 **`--dry-run=client -o yaml > 파일이름.yaml`** 마법의 주문을 붙여서 **쿠버네티스가 직접 오타 없는 YAML 뼈대를 만들어주게** 시킵니다!
  * `--dry-run=client`: "실제로 클러스터에 만들진 말고 시늉만 해!"
  * `-o yaml`: "그 결과를 YAML 양식 글자로 화면에 출력해 줘!"
  * `> 파일.yaml`: "화면에 나온 글자를 파일로 바로 저장해!"

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 쿠버네티스 공식 문서 (`https://kubernetes.io/ko/docs/` — CKA 시험장 유일한 오픈북 사이트!)**:
  1. 검색창에 **`"kubectl 치트 시트"`** (영문: **`"kubectl cheat sheet"`**) 검색!
     * 시험장에서 가장 먼저 열어두는 페이지입니다. 여기서 `kubectl run` 명령어와 `-o yaml`, `--dry-run=client` 예제를 눈으로 확인해 보세요.
* **📘 FastAPI 공식 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  2. **`배포 (Deployment)` → `컨테이너 안의 FastAPI - Docker`**
     * 맨 아래쪽 공식 `Dockerfile` 예제(`FROM python:...`, `WORKDIR`, `COPY`, `RUN pip install`, `CMD`)가 어떻게 생겼는지 구경해 보세요!
* **💻 터미널 내장 컨닝법 (`--help`)**:
  * 명령어가 기억 안 날 땐 언제든 터미널에 `kubectl run --help`를 치면 맨 위에 예제 코드가 그대로 나옵니다!

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 1-1] 내 윈도우 PC에서 Docker와 로컬 쿠버네티스 켜기

1. **Docker Desktop 실행 확인**:
   * 윈도우 작업표시줄에 고래 모양 아이콘(**Docker Desktop**)이 켜져 있는지 확인합니다.
2. **Docker Desktop 안에서 로컬 쿠버네티스 활성화하기**:
   * Docker Desktop 창 우측 상단 **톱니바퀴(Settings)** 클릭 ➡️ 왼쪽 메뉴에서 **`Kubernetes`** 클릭!
   * **`Enable Kubernetes`** 체크박스를 체크하고 우측 하단 **`Apply & restart`** 버튼을 누릅니다 (처음 켤 때는 쿠버네티스 엔진을 다운로드하느라 2~3분 정도 걸립니다).
3. **터미널에서 연결 확인하기**:
   VS Code 터미널에서 아래 명령어를 쳤을 때 `docker-desktop` 노드가 **`Ready`**로 나오는지 확인해 보세요!
   ```powershell
   kubectl get nodes
   ```
   *(만약 Docker Desktop 대신 다른 환경을 쓰고 계시거나 아직 Docker가 안 깔려 있다면 에이전트에게 바로 말씀해 주세요!)*

---

### [Step 1-2] 우리 FastAPI 앱을 포장하는 `Dockerfile` 만들기

1. 먼저 `requirements.txt` 파일을 열어 `httpx2` 줄은 지우거나 그대로 두되, 표준 파이썬 3.12 컨테이너에서 깔끔하게 설치되도록 아래 목록이 있는지 확인합니다 (`python:3.12-slim`에서는 `PyYAML`도 에러 없이 1초 만에 바로 깔립니다!):
2. 프로젝트 루트(`c:\Users\332br\workspace\cascade-ecosystem\Dockerfile`)에 확장자 없는 **`Dockerfile`** 파일을 새로 만들고 아래 6줄을 작성해 보세요:
   ```dockerfile
   FROM python:3.12-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app ./app

   CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
   *(💡 왜 `--host 0.0.0.0`을 쓸까요? 기본값 `127.0.0.1`로 띄우면 컨테이너 상자 안에서만 접속되고 바깥(쿠버네티스)에서 접속이 안 됩니다! 컨테이너로 띄울 땐 무조건 `0.0.0.0`(모든 문 열기)이 필수입니다!)*
3. **도커 이미지(밀키트 상자) 빌드하기**:
   터미널에서 아래 명령어를 실행해 이미지를 만듭니다 (맨 끝에 마침표 `.` 필수!):
   ```powershell
   docker build -t kube-pipeline-api:v1 .
   ```

---

### [Step 1-3] CKA 실전 기법으로 첫 파드 YAML 뽑고 띄우기!

1. **명령어로 YAML 뼈대 자동 생성하기 (`--dry-run=client -o yaml`)**:
   터미널에서 아래 명령어를 실행해 보세요:
   ```powershell
   kubectl run pipeline-pod --image=kube-pipeline-api:v1 --port=8000 --image-pull-policy=Never --dry-run=client -o yaml > k8s/01-cluster-setup/first-pod.yaml
   ```
   *(💡 `--image-pull-policy=Never`란? 쿠버네티스에게 "이 이미지는 인터넷(Docker Hub)에서 찾지 말고, 방금 내 컴퓨터에서 `docker build`로 만든 걸 그대로 써!"라고 알려주는 옵션입니다.)*
2. **생성된 `k8s/01-cluster-setup/first-pod.yaml` 파일 눈으로 구경하기**:
   * VS Code에서 해당 파일을 열어보세요!
   * 어제 Step 8 파이썬 코드에서 봤던 `apiVersion`, `kind`, `metadata`, `spec`, `containers`, `image`, `name`이 똑같이 적혀 있는 게 보이시나요? 😮
3. **쿠버네티스에 실제로 파드 배포하기 (`kubectl apply`)**:
   ```powershell
   kubectl apply -f k8s/01-cluster-setup/first-pod.yaml
   ```
4. **내 파드가 잘 떴는지(`Running`) 확인하기**:
   ```powershell
   kubectl get pods
   ```
   `STATUS`가 **`Running`**(`1/1`)으로 뜨면 대성공입니다!
5. **(보너스) 쿠버네티스 파드 안의 FastAPI에 접속해 보기!**:
   ```powershell
   kubectl port-forward pod/pipeline-pod 8080:8000
   ```
   위 명령어를 켜둔 채로 브라우저에서 `http://127.0.0.1:8080/healthz` 또는 `http://127.0.0.1:8080/docs` 에 들어가면, **쿠버네티스 파드 안에서 돌아가는 내 FastAPI 서버**가 응답합니다! (확인 후 터미널에서 `Ctrl + C`로 종료)

---

## 4️⃣ 완료 및 체크 요청
여기까지 진행해 보시고:
* 아직 Docker Desktop이 안 켜져 있거나 설정 중 막히면 언제든 말씀해 주시고,
* 파드가 `Running`으로 떴다면 **"CKA 미션 1 다 했어, 체크해줘!"**라고 말씀해 주세요!
