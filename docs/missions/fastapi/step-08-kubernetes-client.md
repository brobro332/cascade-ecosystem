# 🎯 [FastAPI Mission 08 — 최종 관문] 공식 `kubernetes` Python Client로 K8s `Job` 동적 생성하기

> **난이도**: ★★★★☆ (중상급 — FastAPI 트랙과 CKA 트랙이 하나로 만나는 하이라이트!)  
> **연계 CKA 개념**: `batch/v1` `Job` 매니페스트 구조(`restartPolicy: Never`, `backoffLimit`, `ttlSecondsAfterFinished`), In-Cluster `ServiceAccount` 인증 및 RBAC  
> **작업 대상 파일**: `requirements.txt`, `app/api/k8s_client.py` (신규), `app/api/main.py`, `tests/test_api.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. 왜 `BackgroundTasks` 말고 쿠버네티스 `Job`을 코드로 생성할까요?
* Step 7에서 배운 `BackgroundTasks`는 **API 서버(`pipeline-api`) 파드 내부**에서 돌아갑니다.
* 만약 가벼운 작업이 아니라 **수백 페이지짜리 무거운 PDF 분석**이 들어오면 어떻게 될까요? API 서버의 CPU와 메모리가 꽉 차서 다른 손님들의 요청까지 느려집니다!
* 그래서 실전 쿠버네티스 아키텍처에서는:
  1. 무거운 작업이 들어오면 `pipeline-api`가 **쿠버네티스 대장(`kube-apiserver`)에게 전화를 걸어(`kubernetes` Python SDK)**:
  2. **"대장님! 이 파일만 전문으로 처리하고 스스로 사라지는 일회용 작업 파드(`K8s Job`) 하나만 고성능 워커 노드(노트북)에 새로 띄워주세요!"**라고 요청합니다.

---

### 💡 2. 파이썬 `V1Job` 객체 = 쿠버네티스 `Job` YAML과 100% 쌍둥이! (CKA 시험 직결!)
곧 시작할 CKA 트랙에서 가장 자주 마주칠 **`Job` YAML 구조**와 오늘 작성할 파이썬 코드는 모양이 완전히 똑같습니다:

| 쿠버네티스 YAML 필드 (CKA 시험) | 공식 `kubernetes` 파이썬 클래스 | 역할 |
| :--- | :--- | :--- |
| `apiVersion: batch/v1`<br>`kind: Job` | `client.V1Job(...)` | 일회성 배치 작업 리소스 선언 |
| `metadata: name: ...` | `client.V1ObjectMeta(name=...)` | Job의 이름과 네임스페이스 지정 |
| `spec: ttlSecondsAfterFinished: 300` | `client.V1JobSpec(ttl_seconds_after_finished=300, ...)` | 작업 완료 후 300초 뒤 파드 자동 청소 |
| `spec.template.spec.restartPolicy: Never` | `client.V1PodSpec(restart_policy="Never", ...)` | **(CKA 필수 규칙!)** Job 파드는 절대 `Always`를 쓸 수 없음 (`Never` 또는 `OnFailure`만 가능!) |
| `spec.template.spec.containers: [...]` | `client.V1Container(name=..., image=..., command=[...])` | 실제로 실행할 워커 컨테이너와 명령어 |

---

### 💡 3. 아직 쿠버네티스 클러스터가 없는데 로컬에서 어떻게 돌려보나요?
바로 우리가 **Step 6에서 배운 `Depends` ("갈아끼우는 플러그")** 덕분입니다!
* `build_k8s_job_manifest(...)` 함수는 로컬에서도 **진짜 `kubernetes.client.V1Job` 객체**를 조립합니다.
* 실제로 클러스터에 전송하는 부분(`K8sJobDispatcher`)만 `Depends` 플러그로 꽂아두면, 클러스터가 없는 내 노트북에서도 `V1Job` 매니페스트가 CKA 규격에 맞게 완벽히 조립되었는지 100% 검증할 수 있습니다!

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 쿠버네티스 공식 문서 (`https://kubernetes.io/ko/docs/` — CKA 오픈북 허용 사이트!)**:
  * 검색창에 **`"Jobs"`** 검색 → **`개념 (Concepts) > 워크로드 > 컨트롤러 > 잡(Jobs)`**
  * **꼭 눈으로 확인할 부분**:
    * 예제 YAML에서 `apiVersion: batch/v1`, `kind: Job` 구조 확인
    * `spec.template.spec.restartPolicy: Never` 위치 확인!
* **🐍 공식 Python Kubernetes Client**:
  * 검색 키워드: `"kubernetes python client V1Job create_namespaced_job example"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 8-1] 공식 `kubernetes` 파이썬 클라이언트 설치
1. 가상환경(`(.venv)`) 터미널에서 설치:
   ```powershell
   pip install kubernetes
   ```
2. `requirements.txt` 마지막 줄에 `kubernetes`를 추가해 주세요.

---

### [Step 8-2] `app/api/k8s_client.py` 새로 만들기

쿠버네티스 `V1Job` 매니페스트 객체를 조립하고 클러스터(또는 로컬 시뮬레이터)로 전송하는 모듈을 만듭니다.  
`app/api/k8s_client.py` 파일을 생성하고 아래 코드를 작성해 보세요:

```python
from kubernetes import client, config
from app.api.schemas import JobCreateRequest


def build_k8s_job_object(job_id: str, job_req: JobCreateRequest) -> client.V1Job:
    """
    JobCreateRequest를 받아 쿠버네티스 표준 batch/v1 V1Job 매니페스트 객체를 조립합니다.
    (CKA 시험의 Job YAML 구조와 1:1로 매칭됩니다!)
    """
    # 1. 실제로 일을 할 컨테이너 정의 (spec.template.spec.containers[0])
    container = client.V1Container(
        name="heavy-worker",
        image="kube-pipeline-worker:latest",
        command=["python", "-m", "app.worker.cli", "--file", job_req.target_file, "--task", job_req.task_type.value],
    )

    # 2. 파드 스펙 정의 (주의: Job의 restart_policy는 반드시 'Never' 또는 'OnFailure'!)
    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        containers=[container],
    )

    # 3. 파드 템플릿 및 Job 스펙 정의
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "kube-pipeline-job", "job_id": job_id}),
        spec=pod_spec,
    )
    job_spec = client.V1JobSpec(
        template=template,
        backoff_limit=2,
        ttl_seconds_after_finished=300,
    )

    # 4. 최종 V1Job 객체 반환
    return client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_id),
        spec=job_spec,
    )


class K8sJobDispatcher:
    """K8s 클러스터에 Job을 생성하는 디스패처 (Depends 주입 대상)"""

    def dispatch(self, namespace: str, k8s_job: client.V1Job) -> str:
        # 실제 클러스터 연결 시: ServiceAccount(In-Cluster) 또는 로컬 kubeconfig 로드
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        batch_v1 = client.BatchV1Api()
        created = batch_v1.create_namespaced_job(namespace=namespace, body=k8s_job)
        return created.metadata.name


def get_k8s_dispatcher() -> K8sJobDispatcher:
    return K8sJobDispatcher()
```

---

### [Step 8-3] `app/api/main.py`에 K8s 배치 Job 생성 엔드포인트(`POST /jobs/k8s`) 추가

1. `app/api/main.py` 상단에 방금 만든 모듈을 import 합니다:
   ```python
   from app.api.k8s_client import K8sJobDispatcher, build_k8s_job_object, get_k8s_dispatcher
   ```
2. 파일 맨 아래에 **`POST /jobs/k8s`** 엔드포인트를 추가합니다:
   ```python
   @app.post("/jobs/k8s", status_code=201)
   def create_k8s_batch_job(
       job_req: JobCreateRequest,
       dispatcher: K8sJobDispatcher = Depends(get_k8s_dispatcher),
   ) -> JobResponse:
       new_id = f"k8s-job-{uuid.uuid4().hex[:8]}"

       # 1. CKA 표준 규격의 V1Job 매니페스트 객체 조립
       k8s_job = build_k8s_job_object(new_id, job_req)

       # 2. Depends로 주입된 dispatcher를 통해 kube-pipeline 네임스페이스에 배포 요청!
       dispatched_name = dispatcher.dispatch(namespace="kube-pipeline", k8s_job=k8s_job)

       new_job = JobResponse(
           job_id=dispatched_name,
           task_type=job_req.task_type,
           target_file=job_req.target_file,
           priority=job_req.priority,
           status=JobStatus.PROCESSING,
           message=f"Dispatched to Kubernetes Job '{dispatched_name}' in namespace 'kube-pipeline'",
       )
       jobs_db[new_id] = new_job
       return new_job
   ```

---

### [Step 8-4] `tests/test_api.py`에서 가짜 K8s 클러스터(`dependency_overrides`)로 검증하기!

Step 6에서 질문하셨던 **"왜 `Depends`로 갈아끼우는 구조를 만드나요?"**의 진가를 직접 눈으로 확인할 차례입니다!  
아직 쿠버네티스 클러스터가 내 PC에 안 떠 있지만, `get_k8s_dispatcher`를 가짜(Fake) 디스패처로 갈아끼워서 **내가 조립한 `V1Job` 매니페스트가 CKA 규칙(`restart_policy == "Never"`, 컨테이너 이미지, 네임스페이스)에 맞는지** 완벽하게 테스트할 수 있습니다!

1. `tests/test_api.py` 상단에 `from app.api.k8s_client import get_k8s_dispatcher`를 추가합니다.
2. 맨 아래에 10번째 테스트 함수 `test_create_k8s_batch_job_with_mock_dispatcher()`를 추가해 보세요:
   ```python
   def test_create_k8s_batch_job_with_mock_dispatcher():
       captured = {}

       class FakeK8sDispatcher:
           def dispatch(self, namespace: str, k8s_job) -> str:
               # API가 넘겨준 네임스페이스와 V1Job 객체를 가로채서 기록!
               captured["namespace"] = namespace
               captured["k8s_job"] = k8s_job
               return k8s_job.metadata.name

       app.dependency_overrides[get_k8s_dispatcher] = lambda: FakeK8sDispatcher()

       try:
           res = client.post(
               "/jobs/k8s",
               json={"task_type": "summary", "target_file": "manual.pdf", "priority": 5},
           )
           assert res.status_code == 201
           assert res.json()["status"] == "processing"

           # 조립된 쿠버네티스 V1Job 매니페스트 정밀 검사!
           assert captured["namespace"] == "kube-pipeline"
           v1_job = captured["k8s_job"]
           assert v1_job.api_version == "batch/v1"
           assert v1_job.kind == "Job"
           assert v1_job.spec.template.spec.restart_policy == "Never"
           assert v1_job.spec.template.spec.containers[0].name == "heavy-worker"
       finally:
           app.dependency_overrides.clear()
   ```
3. 터미널에서 `pytest -v`를 실행해 **`10 passed`**를 달성해 보세요!

---

## 4️⃣ 완료 및 체크 요청
`10 passed`가 뜨면 **"미션 8 다 했어, 체크해줘!"**라고 말씀해 주세요!  
이 미션을 통과하면 **FastAPI 트랙(Step 1~8) 전 과정 수료**입니다! 🎉
