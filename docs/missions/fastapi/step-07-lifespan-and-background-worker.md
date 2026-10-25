# 🎯 [FastAPI Mission 07] Lifespan 관리 (`/readyz`) & 백그라운드 워커 (`BackgroundTasks`)

> **난이도**: ★★★☆☆ (중급 — 실전 비동기 파이프라인 완성!)  
> **연계 CKA 개념**: `livenessProbe`(`GET /healthz`) vs `readinessProbe`(`GET /readyz`) 차이점, 파드 Graceful Shutdown, 워커 컨테이너 역할 분리  
> **작업 대상 파일**: `app/worker/processor.py` (신규), `app/api/main.py`, `tests/test_api.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. `BackgroundTasks` — 왜 손님을 세워두지 않고 번호표(`PENDING`)부터 줄까요?
지금까지는 `POST /jobs`나 `POST /jobs/upload`로 작업을 등록하면 상태가 영원히 **`pending` (대기 중)**으로만 남아 있었습니다.  
만약 50페이지짜리 PDF 요약이나 고화질 이미지 변환을 `upload_job` 안에서 바로 처리하느라 10초가 걸린다면, 사용자는 10초 동안 화면이 멈춘 채 기다려야 합니다.

그래서 실무 파이프라인은 이렇게 동작합니다:
1. 손님이 파일을 올리면 ➡️ **0.01초 만에 "접수 완료(`status: pending`)!" 번호표를 먼저 주고 응답을 끝냅니다.**
2. 손님이 돌아간 직후 ➡️ **FastAPI의 `BackgroundTasks`(백그라운드 작업자)**가 뒤에서 조용히 `app/worker/processor.py` 함수를 실행해 파일을 처리하고, 작업 상태를 **`completed` (완료)**로 업데이트합니다!
3. 손님이 다시 `GET /jobs/{job_id}`를 조회하면 ➡️ 상태가 **`completed`**로 바뀌어 있습니다!

---

### 💡 2. `lifespan`과 `/readyz` (CKA 시험 단골: Liveness vs Readiness!)
* **`lifespan` (`@asynccontextmanager`)**:
  * 식당이 **문을 열기 직전(`yield` 위쪽 코드)**에 주방 기구를 예열(폴더 생성, DB/큐 연결 준비)하고,
  * 영업이 끝나고 **문을 닫을 때(`yield` 아래쪽 코드)** 가스불을 끄고 정리(연결 종료)하는 FastAPI 공식 수명주기 관리 문법입니다.
* **CKA 필수 개념 — 왜 `/healthz` 말고 `/readyz`를 또 만드나요?**
  * **`/healthz` (Liveness Probe)**: "서버 프로그램이 멈추지(Hang) 않고 살아있니?" ➡️ 실패하면 쿠버네티스가 **파드를 강제 재시작(Restart)**합니다.
  * **`/readyz` (Readiness Probe)**: "주방 예열(초기화, 스토리지/큐 연결)이 다 끝나서 **지금 손님 주문을 받을 준비가 됐니?**" ➡️ 실패하면 파드를 죽이진 않고, 준비될 때까지 **손님(Service 트래픽)만 안 보냅니다!**

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  1. **`자습서 - 사용자 가이드` → `백그라운드 작업 (Background Tasks)`**:
     * `from fastapi import BackgroundTasks` import 방법
     * 엔드포인트 매개변수에 `background_tasks: BackgroundTasks`를 선언하고 `background_tasks.add_task(함수이름, 인자1, 인자2)`로 뒷방 작업을 예약하는 법!
  2. **`고급 사용자 가이드 (Advanced User Guide)` → `수명 주기 이벤트 (Lifespan Events)`**:
     * `from contextlib import asynccontextmanager`와 `@asynccontextmanager`를 사용해 `async def lifespan(app: FastAPI):`를 만들고 `yield`를 쓰는 패턴!
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi BackgroundTasks add_task 사용법"`
  * `"fastapi lifespan asynccontextmanager 예제"`
  * `"kubernetes livenessProbe readinessProbe 차이"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 7-1] 백그라운드 워커 모듈 `app/worker/processor.py` 새로 만들기

실제로 작업을 처리해 상태를 `PENDING` ➡️ `COMPLETED`로 바꿔주는 워커 함수를 `app/worker/processor.py`에 작성합니다.

1. `app/worker/processor.py` 파일을 새로 생성합니다.
2. 아래 코드를 참고하여 작성해 보세요 (어떤 노드와 CPU 아키텍처가 처리했는지 메시지에 기록합니다!):
   ```python
   import platform
   from app.api.schemas import JobResponse, JobStatus

   def process_job_in_background(
       job_id: str,
       jobs_db: dict[str, JobResponse],
       node_name: str = "local-dev-node",
   ) -> None:
       """백그라운드에서 작업을 처리하고 상태를 COMPLETED로 변경하는 워커 함수"""
       if job_id not in jobs_db:
           return

       job = jobs_db[job_id]
       arch = platform.machine()  # 예: AMD64, ARM64 (라즈베리파이)

       # 처리 완료 상태로 업데이트된 새 JobResponse 저장
       jobs_db[job_id] = job.model_copy(
           update={
               "status": JobStatus.COMPLETED,
               "message": f"Processed [{job.task_type.value}] on {node_name} ({arch})",
           }
       )
   ```
   *(💡 Pydantic v2 팁: `model_copy(update={...})`를 쓰면 기존 모델의 나머지 필드는 그대로 두고 원하는 필드만 깔끔하게 바꾼 복사본을 만들 수 있습니다!)*

---

### [Step 7-2] `app/api/main.py`에 `lifespan` 및 `GET /readyz` 추가하기

1. `app/api/main.py` 상단에 필요한 모듈을 import 합니다:
   ```python
   from contextlib import asynccontextmanager
   from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Depends, BackgroundTasks
   from app.worker.processor import process_job_in_background
   ```
2. `app = FastAPI(...)` 선언 **바로 위에** `lifespan` 함수를 정의하고 `FastAPI(lifespan=lifespan)`으로 연결합니다:
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # [Startup] 서버 시작 시 업로드 폴더 미리 생성 및 준비 완료 표시
       settings = get_settings()
       settings.upload_dir.mkdir(parents=True, exist_ok=True)
       app.state.is_ready = True
       yield
       # [Shutdown] 서버 종료 시 정리
       app.state.is_ready = False

   app = FastAPI(lifespan=lifespan)
   app.state.is_ready = True  # TestClient 기본 호환용 초기값
   ```
3. **`GET /readyz` (Readiness Probe 엔드포인트)**를 `/healthz` 바로 아래에 추가합니다:
   * 만약 `not getattr(app.state, "is_ready", False)` 이면 ➡️ `raise HTTPException(status_code=503, detail="Service not ready")` (`503 Service Unavailable`)
   * 준비 상태라면 ➡️ `return {"status": "ready"}`

---

### [Step 7-3] `POST /jobs`와 `POST /jobs/upload`에 `BackgroundTasks` 연결하기

작업이 등록되자마자 백그라운드 워커(`process_job_in_background`)가 실행되도록 연결합니다!

1. **`POST /jobs` (`create_job`) 수정**:
   * 함수 매개변수에 `background_tasks: BackgroundTasks`와 `settings: Settings = Depends(get_settings)`를 추가합니다:
     ```python
     @app.post("/jobs", status_code=201)
     def create_job(
         job_req: JobCreateRequest,
         background_tasks: BackgroundTasks,
         settings: Settings = Depends(get_settings),
     ) -> JobResponse:
     ```
   * `jobs_db[new_id] = new_job` 바로 아래(`return new_job` 직전)에 백그라운드 작업을 등록합니다:
     ```python
     background_tasks.add_task(process_job_in_background, new_id, jobs_db, settings.node_name)
     ```
2. **`POST /jobs/upload` (`upload_job`) 수정**:
   * 매개변수에 `background_tasks: BackgroundTasks`를 추가합니다 (주의: 기본값 `= ...`이 없는 매개변수이므로 `file: UploadFile = ...` 보다 **앞쪽(첫 번째 인자)**에 두거나, 맨 뒤에 둘 필요 없이 첫 번째 줄에 적으면 파이썬 문법 에러가 나지 않습니다!):
     ```python
     @app.post("/jobs/upload", status_code=201)
     async def upload_job(
         background_tasks: BackgroundTasks,
         file: UploadFile = File(..., description="업로드할 원본 파일"),
         task_type: TaskType = Form(default=TaskType.RESIZE, description="작업 종류"),
         priority: int = Form(default=3, ge=1, le=5, description="우선순위 (1~5)"),
         settings: Settings = Depends(get_settings),
     ) -> JobResponse:
     ```
   * 마찬가지로 `jobs_db[new_id] = new_job` 바로 아래에 한 줄 추가합니다:
     ```python
     background_tasks.add_task(process_job_in_background, new_id, jobs_db, settings.node_name)
     ```

---

### [Step 7-4] `tests/test_api.py` 확인 및 테스트 추가!

잠깐! 이제 `POST /jobs`를 호출하면 응답 직후 `BackgroundTasks`가 자동으로 실행되어 `jobs_db` 안의 작업 상태가 **`pending`에서 `completed`로 즉시 바뀝니다!**

1. **기존 테스트(`test_list_jobs_filter_and_limit`) 변화 확인**:
   * 기존 `test_list_jobs_filter_and_limit()`에서는 작업 2개를 만든 뒤 `status=pending`이 2개, `status=completed`가 0개일 거라고 검증했었죠?
   * 이제는 백그라운드 워커가 일을 끝내놓기 때문에 **`status=completed`가 2개, `status=pending`이 0개**가 됩니다!
   * `test_list_jobs_filter_and_limit()` 안의 `assert` 숫자를 백그라운드 처리가 반영된 결과(`pending` 0개, `completed` 2개)에 맞게 수정해 주세요!
2. **신규 테스트 `test_readyz_and_background_worker()` 추가**:
   * `GET /readyz`가 `200`과 `{"status": "ready"}`를 반환하는지 검증
   * `POST /jobs`로 작업을 만든 직후에는 응답의 `status == "pending"`이지만, 이어서 `GET /jobs/{job_id}`로 다시 조회했을 때는 백그라운드 워커 덕분에 **`status == "completed"`**로 바뀌어 있는지 검증!
3. 터미널에서 `pytest -v`를 실행해 **`9 passed`**가 뜨는지 확인해 보세요!

---

## 4️⃣ 완료 및 체크 요청
`9 passed`를 확인하셨다면 **"미션 7 다 했어, 체크해줘!"**라고 말씀해 주세요!
