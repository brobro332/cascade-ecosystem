# 🎯 [FastAPI Mission 05] 비동기 원리 (`async def` vs `def`) & 실제 파일 업로드 구현

> **난이도**: ★★★☆☆ (중급 — 실무 핵심!)  
> **연계 CKA 개념**: 파드 내부에서 공유 스토리지 볼륨(`PersistentVolumeClaim` 마운트 경로 `/app/storage/uploads`)에 파일을 읽고 쓰는 구조  
> **작업 대상 파일**: `requirements.txt`, `.gitignore`, `app/api/main.py`, `tests/test_api.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. `async def` vs `def` — 언제 무엇을 써야 하나요? (면접/실무 단골!)
지금까지는 함수를 만들 때 그냥 `def create_job():` 처럼 썼습니다. 그런데 FastAPI 공식 문서를 보면 어떤 곳은 **`async def`**를 쓰고 어떤 곳은 **`def`**를 씁니다. 차이가 뭘까요?

* **식당 웨이터 비유**:
  * **`async def` (비동기 코루틴 — 슈퍼 웨이터 1명)**:
    * 손님이 주문을 하거나 파일이 네트워크를 타고 다 들어올 때까지(`await file.read()`) 웨이터가 그 자리에서 멍하니 기다리지 않고, **"잠깐 다른 손님 주문 먼저 받고 올게요(`await`)!"** 하며 동시에 수백 명을 상대합니다.
    * **⚠️ 치명적 주의점**: 만약 `async def` 안에서 `await`가 없는 느린 작업(예: `time.sleep(5)`나 무거운 이미지 변환)을 직접 실행하면, 슈퍼 웨이터 1명이 그 자리에서 5초 동안 얼어붙어 **가게 전체(모든 다른 사용자의 요청)가 멈춰버립니다(Event Loop Blocking)!**
  * **`def` (일반 동기 함수 — 보조 스레드풀 활용)**:
    * `def`로 선언하면 FastAPI가 알아서 **"이건 `await`를 안 쓰는 일반 작업이네? 메인 웨이터가 멈추면 안 되니까 뒤쪽 보조 알바생(ThreadPool)에게 시켜야겠다!"** 하고 별도 스레드에서 안전하게 돌려줍니다.
* **오늘의 핵심 공식**:
  * 내부에서 **`await`를 쓰는 비동기 함수**(오늘 배울 `await file.read()`)를 호출할 때는 👉 **`async def`** 선언!
  * `await` 없이 동작하는 일반 파이썬 코드를 실행할 때는 👉 **`def`** 선언!

### 💡 2. `UploadFile`과 공유 스토리지(`storage/uploads`)
* Step 2~4에서는 파일 이름(`"photo.png"`)만 글자로 받았지만, 이제 진짜 이미지/문서 파일 바이트를 업로드 받습니다.
* 로컬 개발 PC에서는 프로젝트 안의 `storage/uploads/` 폴더에 저장하고, 나중에 쿠버네티스(CKA)에 올릴 때는 이 `storage/uploads/` 경로에 **공유 볼륨(PVC)**을 마운트해서 워커 파드(`media-worker`)가 같은 파일을 꺼내 작업하게 됩니다!

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  1. **`비동기 (Async)` (`https://fastapi.tiangolo.com/ko/async/`)**: 유명한 '버거 가게 이야기'로 설명된 `async`와 `await` 원리 (시간 날 때 꼭 읽어보세요!)
  2. **`자습서 - 사용자 가이드` → `요청 파일 (Request Files)`**:
     * `from fastapi import File, UploadFile` 사용법
     * `async def` 안에서 `contents = await file.read()`로 파일 바이트를 읽는 법과 `file.filename` 속성 확인
  3. **`자습서 - 사용자 가이드` → `요청 파일과 폼 데이터 (Request Forms and Files)`**:
     * 파일(`UploadFile = File(...)`)과 추가 옵션(`Form(...)`)을 한 엔드포인트에서 동시에 받는 방법!
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi UploadFile Form 같이 받기"`
  * `"python pathlib Path mkdir write_bytes 파일 저장"`
  * `"fastapi TestClient 파일 업로드 files data 테스트"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 5-1] 파일 업로드용 필수 패키지(`python-multipart`) 설치
HTTP 프로토콜에서 파일은 JSON이 아니라 `multipart/form-data`라는 형식으로 전송됩니다. 이를 해석하려면 `python-multipart`가 필요합니다.

1. 가상환경(`(.venv)`)이 켜진 터미널에서 설치:
   ```powershell
   pip install python-multipart
   ```
2. `requirements.txt` 마지막 줄에 `python-multipart`를 추가해 주세요.
3. `.gitignore` 파일 끝에 업로드 임시 폴더인 `storage/`를 한 줄 추가해 주세요 (테스트할 때 생기는 파일이 Git에 커밋되지 않도록!).

---

### [Step 5-2] `app/api/main.py`에 파일 업로드 엔드포인트(`POST /jobs/upload`) 추가

1. **상단 import 추가**:
   * 파이썬 내장 경로 도구: `from pathlib import Path`
   * FastAPI 파일/폼 도구: `from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form`
   * 스키마에서 `TaskType`도 함께 import: `from app.api.schemas import JobCreateRequest, JobResponse, JobStatus, TaskType`
2. **저장 폴더 경로 상수 선언** (`jobs_db` 바로 아래쯤):
   ```python
   UPLOAD_DIR = Path("storage/uploads")
   ```
3. **`POST /jobs/upload` 비동기 엔드포인트 구현 (`async def` 사용!)**:
   * 데코레이터: `@app.post("/jobs/upload", status_code=201)`
   * 함수 시그니처:
     ```python
     async def upload_job(
         file: UploadFile = File(..., description="업로드할 원본 파일"),
         task_type: TaskType = Form(default=TaskType.RESIZE, description="작업 종류"),
         priority: int = Form(default=3, ge=1, le=5, description="우선순위 (1~5)")
     ) -> JobResponse:
     ```
   * **함수 내부 구현 순서 (직접 작성해 보세요!)**:
     1. `contents = await file.read()` 로 업로드된 파일의 바이트 데이터를 비동기로 읽습니다.
     2. **빈 파일(0바이트) 검증**: 만약 `len(contents) == 0`(또는 `not contents`)이면:
        `raise HTTPException(status_code=400, detail="Empty file is not allowed")` 를 발생시킵니다.
     3. **디스크에 파일 저장**:
        * 폴더가 없으면 자동 생성: `UPLOAD_DIR.mkdir(parents=True, exist_ok=True)`
        * 저장할 경로 만들기: `file_path = UPLOAD_DIR / file.filename`
        * 바이트 쓰기: `file_path.write_bytes(contents)`
     4. **작업 등록 및 반환**:
        * 기존 `create_job`처럼 `new_id = f"job-{uuid.uuid4().hex[:8]}"`를 만들고,
        * `JobResponse` 객체(`target_file=file.filename`, `status=JobStatus.PENDING`, `message="File uploaded and job submitted"`)를 생성해 `jobs_db[new_id]`에 저장한 뒤 반환합니다!

---

### [Step 5-3] `tests/test_api.py`에 파일 업로드 자동 테스트 2개 추가

Swagger UI(`/docs`)에서도 파일을 직접 선택해 업로드해 볼 수 있지만, 우리가 Step 4에서 배운 `pytest`로도 파일 업로드를 자동 검증해 봅시다!  
`tests/test_api.py` 맨 아래에 다음 두 테스트 함수를 추가해 보세요:

1. **`test_upload_job_success()`**:
   * `TestClient`로 파일을 보낼 때는 `json=...` 대신 **`files=...`와 `data=...`(Form 데이터)**를 사용합니다:
     ```python
     response = client.post(
         "/jobs/upload",
         files={"file": ("test_image.png", b"fake-image-binary-content", "image/png")},
         data={"task_type": "watermark", "priority": "1"},
     )
     ```
   * 검증(`assert`)할 것:
     * `response.status_code == 201`
     * `response.json()["target_file"] == "test_image.png"`
     * `response.json()["task_type"] == "watermark"`
     * 실제로 `Path("storage/uploads/test_image.png").exists()`가 `True`인지 확인!
2. **`test_upload_empty_file_returns_400()`**:
   * 빈 바이트(`b""`)를 가진 파일 `files={"file": ("empty.txt", b"", "text/plain")}`을 `/jobs/upload`에 전송했을 때:
   * `response.status_code == 400` 인지 검증!

---

### [Step 5-4] `pytest -v` 실행해서 7개 테스트 모두 통과시키기!
터미널에서 `pytest -v`를 실행해 기존 5개 + 신규 2개 = **`7 passed`**가 뜨는지 확인해 보세요!

---

## 4️⃣ 완료 및 체크 요청
`7 passed`를 확인하셨다면 **"미션 5 다 했어, 체크해줘!"**라고 말씀해 주세요!
