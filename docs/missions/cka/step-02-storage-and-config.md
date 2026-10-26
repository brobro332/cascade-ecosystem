# 🎯 [CKA Mission 02] `Namespace`, `ConfigMap`, `Secret` 주입 및 `PV`/`PVC` 볼륨 마운트

> **난이도**: ★★☆☆☆ (CKA 필수 기본기!)  
> **CKA 출제 비중**: Storage (10%) + Workloads Configuration (핵심 빈출!)  
> **연계 FastAPI 코드**: Step 6에서 만든 `app/api/config.py` (`Settings`의 `node_name`, `upload_dir`이 K8s `ConfigMap`으로 자동 덮어써지는 마법 체험!)  
> **작업 대상 폴더**: `k8s/02-storage-config/`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. `Namespace` (`kube-pipeline`) — 왜 아파트 동(101동, 102동)을 나눌까요?
* 미션 1에서 띄운 `pipeline-pod`는 아무 구역을 지정하지 않아서 기본 구역(`default` 네임스페이스)에 만들어졌습니다.
* 회사나 CKA 시험장에서는 수십 개의 프로그램이 한 클러스터에서 돌아가기 때문에, 이름표를 붙인 전용 구역(**`Namespace`: `kube-pipeline`**)을 만들어 그 안에만 우리 파드들을 모아둡니다.
* **⚠️ CKA 시험 주의사항 1순위**: 시험 문제의 95%는 *"네임스페이스 `xxx`에 생성하시오"*라고 나옵니다. 명령어에 **`-n kube-pipeline`**을 빼먹으면 문제를 다 풀고도 **0점 처리**됩니다!

---

### 💡 2. `ConfigMap` & `Secret` — 코드 수정 없이 환경변수 찔러 넣기!
* 우리가 FastAPI Step 6에서 `app/api/config.py`에 이렇게 적었던 걸 기억하시나요?
  ```python
  class Settings(BaseSettings):
      app_name: str = "kube-pipeline-api"
      upload_dir: Path = Path("storage/uploads")
      node_name: str = "local-dev-node"
  ```
* 쿠버네티스에서는 **`ConfigMap`(일반 설정 메모장)**에 `NODE_NAME: k8s-local-cluster`라고 적어 파드에 연결해주면, 우리 FastAPI 앱이 켜질 때 `"local-dev-node"` 대신 **`"k8s-local-cluster"`**를 자동으로 읽어옵니다!
* 비밀번호나 토큰처럼 남에게 보이면 안 되는 값은 **`Secret`(암호화/인코딩 금고)**에 담아 주입합니다.

---

### 💡 3. `PV` (PersistentVolume) & `PVC` (PersistentVolumeClaim) — 파드가 죽어도 파일이 안 날아가는 외장하드!
* **파드(`Pod`)는 일회용 원룸**입니다. 파드가 재시작되거나 삭제되면 그 안에 저장된 파일(`storage/uploads`)은 100% 사라집니다.
* 그래서 쿠버네티스는 **2단계 외장하드 대여 시스템**을 씁니다:
  1. **`PV` (PersistentVolume — 외장하드 실물)**: 클러스터 전체에 등록된 실제 디스크 공간 (예: `1Gi` 용량, 노드의 `/tmp/pipeline-data` 폴더 연결)
  2. **`PVC` (PersistentVolumeClaim — 외장하드 대여 신청서)**: 우리 `kube-pipeline` 네임스페이스에서 *"저 1Gi짜리 외장하드 쓰겠습니다!"* 하고 내는 신청서. 조건이 맞으면 `PV`와 `PVC`가 찰떡처럼 붙어서 **`Bound` (연결 완료)** 상태가 됩니다!
  3. **파드 마운트 (`volumeMounts`)**: 대여한 `PVC`를 파드 안의 `/app/storage/uploads` 경로에 꽂아줍니다!

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

CKA 시험장에서도 똑같이 찾을 수 있도록 쿠버네티스 공식 문서(`https://kubernetes.io/ko/docs/`)에서 아래 키워드를 검색해 보세요:

1. **🔍 검색어 1: `"Configure a Pod to Use a ConfigMap"`** (한글: **`"컨피그맵을 사용하도록 파드 구성"`**)
   * 문서 중간의 **`컨피그맵의 모든 키-값 쌍을 컨테이너 환경 변수로 설정`** 섹션에서 `envFrom:` 아래에 `configMapRef:`를 쓰는 짧은 YAML 예제를 눈으로 확인해 보세요!
2. **🔍 검색어 2: `"Configure a Pod to Use a PersistentVolume for Storage"`** (한글: **`"스토리지로 퍼시스턴트볼륨을 사용하도록 파드 구성"`**)
   * 한 페이지 안에 **`PersistentVolume` 생성 → `PersistentVolumeClaim` 생성 → `Pod`에서 `volumes` & `volumeMounts`로 연결**하는 3단계 YAML이 전부 다 나와 있습니다! (CKA 시험 때 그대로 복사해서 이름과 용량만 바꿔 쓰는 1등 컨닝 페이지입니다!)
3. **💻 터미널 `--help` 컨닝법**:
   * `kubectl create configmap --help`
   * `kubectl create secret generic --help`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

> 💡 **꿀팁 (PowerShell 한글/인코딩 깨짐 방지)**: PowerShell에서 `> 파일.yaml`로 저장하면 가끔 인코딩이 `UTF-16`으로 저장되어 한글 주석 등이 깨질 수 있습니다. 아래처럼 명령어로 만든 파일을 VS Code에서 열어 확인해보세요!

### [Step 2-1] `kube-pipeline` 네임스페이스 생성하기
터미널에서 아래 명령어로 네임스페이스 YAML을 뽑고 적용해 보세요:

```powershell
kubectl create namespace kube-pipeline --dry-run=client -o yaml > k8s/02-storage-config/01-namespace.yaml
kubectl apply -f k8s/02-storage-config/01-namespace.yaml
kubectl get ns
```

---

### [Step 2-2] `ConfigMap`과 `Secret`을 명령형 CLI로 1초 만에 만들기!
YAML을 직접 짜지 말고 `--from-literal=키=값` 옵션으로 뽑아냅니다:

1. **`ConfigMap` (`pipeline-config`) 생성**:
   ```powershell
   kubectl create configmap pipeline-config -n kube-pipeline --from-literal=NODE_NAME=k8s-local-cluster --from-literal=UPLOAD_DIR=/app/storage/uploads --dry-run=client -o yaml > k8s/02-storage-config/02-configmap.yaml
   kubectl apply -f k8s/02-storage-config/02-configmap.yaml
   ```
2. **`Secret` (`pipeline-secret`) 생성**:
   ```powershell
   kubectl create secret generic pipeline-secret -n kube-pipeline --from-literal=API_SECRET_KEY=my-super-secret-123 --dry-run=client -o yaml > k8s/02-storage-config/03-secret.yaml
   kubectl apply -f k8s/02-storage-config/03-secret.yaml
   ```
   *(VS Code에서 `03-secret.yaml`을 열어보세요! `my-super-secret-123`이라는 글자가 `bXktc3VwZXItc2VjcmV0LTEyMw==`처럼 Base64로 인코딩되어 저장된 걸 볼 수 있습니다!)*

---

### [Step 2-3] `PV`와 `PVC` 작성해서 `Bound` 시키기! (`04-pv-pvc.yaml`)
`PV`와 `PVC`는 `kubectl create` 단축 명령어가 없어서 공식 문서 예제를 복사해 만듭니다.  
`k8s/02-storage-config/04-pv-pvc.yaml` 파일을 새로 만들고 아래 내용을 작성해 보세요:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pipeline-pv
spec:
  storageClassName: manual
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/tmp/pipeline-data"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-pvc
  namespace: kube-pipeline
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```
*(💡 YAML 파일 하나에 `---` 구분선을 그으면 여러 개의 쿠버네티스 리소스를 한 파일에 같이 적을 수 있습니다!)*

작성 후 배포하고 **`STATUS`가 `Bound`로 뜨는지** 확인합니다:
```powershell
kubectl apply -f k8s/02-storage-config/04-pv-pvc.yaml
kubectl get pv,pvc -n kube-pipeline
```

---

### [Step 2-4] 파드에 `ConfigMap`, `Secret`, `PVC`를 모두 장착해서 띄우기! (`05-pod-storage.yaml`)

`k8s/02-storage-config/05-pod-storage.yaml` 파일을 새로 만들고, 우리 FastAPI 파드에 방금 만든 설정과 외장하드를 연결해 봅시다:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pipeline-storage-pod
  namespace: kube-pipeline
spec:
  containers:
    - name: api
      image: kube-pipeline-api:v1
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
      # 1. ConfigMap과 Secret의 모든 키-값을 환경변수로 한 번에 주입!
      envFrom:
        - configMapRef:
            name: pipeline-config
        - secretRef:
            name: pipeline-secret
      # 2. 컨테이너 안의 /app/storage/uploads 폴더에 외장하드(볼륨) 연결!
      volumeMounts:
        - name: shared-storage
          mountPath: "/app/storage/uploads"
  # 3. 사용할 외장하드(PVC) 신청서 지정
  volumes:
    - name: shared-storage
      persistentVolumeClaim:
        claimName: pipeline-pvc
```

1. 파드를 배포하고 `Running` 상태를 확인합니다 (`-n kube-pipeline` 필수!):
   ```powershell
   kubectl apply -f k8s/02-storage-config/05-pod-storage.yaml
   kubectl get pods -n kube-pipeline
   ```
2. **하이라이트 검증! ConfigMap이 우리 FastAPI의 `Settings`를 진짜로 바꿨는지 확인해 보기**:
   터미널에서 파드 안의 FastAPI(`GET /`)를 직접 찔러보는 명령어를 실행해 보세요:
   ```powershell
   kubectl exec -n kube-pipeline pipeline-storage-pod -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/').read().decode())"
   ```
   출력된 JSON에서 `"node_name"`이 기본값(`"local-dev-node"`)이 아니라 ConfigMap에 적은 **`"k8s-local-cluster"`**로 바뀌어 나오는지 확인해 보세요! 🎉

---

## 4️⃣ 완료 및 체크 요청
1. `kubectl get pv,pvc -n kube-pipeline`에서 `Bound`가 뜨고,
2. `pipeline-storage-pod`가 `Running`이며 `"node_name": "k8s-local-cluster"`가 확인되었다면,  
**"CKA 미션 2 다 했어, 체크해줘!"**라고 말씀해 주세요! (자동 채점 스크립트 `scripts/cka-grade.sh 02` 기준도 함께 통과하게 됩니다!)
