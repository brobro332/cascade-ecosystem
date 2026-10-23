# 🎯 [FastAPI Mission 02] Pydantic v2 데이터 검증 & 스키마 설계

> **난이도**: ★★☆☆☆ (기초~중급)  
> **연계 CKA 개념**: 쿠버네티스 Job/Pod 매니페스트의 엄격한 스키마 검증(`spec.template...`) 및 불량 데이터 차단  
> **작업 대상 파일**: `app/api/schemas.py` (신규 생성), `app/api/main.py` (수정)  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

* **왜 Pydantic과 스키마 분리가 필요한가요?**
  * 사용자가 우리 API 서버에 "이 파일 처리해 줘"라고 요청(JSON)을 보낼 때, 엉뚱한 값(우선순위에 음수를 넣거나, 지원하지 않는 작업 유형을 보내는 등)을 보낼 수 있습니다.
  * 기존 파이썬에서는 `if data.get('priority') < 1:` 처럼 수많은 `if` 문으로 검사해야 했지만, **Pydantic**을 쓰면 타입 힌트(`int`, `str`, `Enum`)만 적어두어도 FastAPI가 **문지기처럼 불량 데이터를 입구컷(`422 Unprocessable Entity`)** 해줍니다.
* **왜 요청(Request)과 응답(Response) 스키마를 따로 만드나요?**
  * 손님이 주문할 때(`JobCreateRequest`)는 `작업 종류`, `파일명`, `우선순위`만 적어서 보냅니다.
  * 서버가 주문서를 접수하고 돌려줄 때(`JobResponse`)는 서버가 직접 발급한 `job_id`, 현재 상태(`status: pending`), `등록 시각` 등이 추가로 포함되어야 합니다.
  * 이 둘을 명확히 분리해야 보안상 안전하고 API 스펙이 깔끔해집니다.

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  * **`자습서 - 사용자 가이드` → `요청 본문 (Request Body)`**
    * `from pydantic import BaseModel` 상속 방법
    * 엔드포인트 함수의 매개변수로 Pydantic 모델을 선언하는 방법 (`def create_job(job: JobCreateRequest):`)
  * **`자습서 - 사용자 가이드` → `응답 모델 - 반환 타입 (Response Model)`**
    * `@app.post("/jobs", response_model=JobResponse, status_code=201)` 사용법
* **🔎 파이썬 표준 라이브러리 & Pydantic**:
  * 파이썬 `enum.Enum` (문자열 Enum): `from enum import Enum`
  * Pydantic `Field`: 값의 범위 제한 (`ge=1, le=5` 등)
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi pydantic basemodel field 사용법"`
  * `"fastapi enum request body validation"`
  * `"fastapi response_model status_code 201"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 2-1] `app/api/schemas.py` 파일 생성하기
`app/api/` 폴더 안에 `schemas.py` 파일을 새로 만들고, 아래 구성 요소를 직접 작성해 보세요:

1. **작업 종류 Enum (`TaskType`)**:
   * 문자열(`str`)과 `Enum`을 다중 상속받아 만듭니다.
   * `RESIZE = "resize"` (이미지 크기 조절)
   * `WATERMARK = "watermark"` (워터마크 삽입)
   * `SUMMARY = "summary"` (문서 요약)
2. **작업 상태 Enum (`JobStatus`)**:
   * `PENDING = "pending"` (대기 중)
   * `PROCESSING = "processing"` (처리 중)
   * `COMPLETED = "completed"` (완료)
   * `FAILED = "failed"` (실패)
3. **요청 스키마 (`JobCreateRequest`)**:
   * `BaseModel` 상속
   * `task_type: TaskType`
   * `target_file: str = Field(..., min_length=1, description="처리 대상 파일명")`
   * `priority: int = Field(default=3, ge=1, le=5, description="우선순위 (1~5, 기본값 3)")`
4. **응답 스키마 (`JobResponse`)**:
   * `BaseModel` 상속
   * `job_id: str`
   * `task_type: TaskType`
   * `target_file: str`
   * `priority: int`
   * `status: JobStatus`
   * `message: str`

---

### [Step 2-2] `app/api/main.py`에 작업 등록 API 추가하기

`app/api/main.py`에 방금 만든 스키마들을 import하고 엔드포인트를 추가합니다:

1. `uuid` 모듈 import: `import uuid`
2. `schemas.py` import:
   ```python
   from app.api.schemas import JobCreateRequest, JobResponse, JobStatus
   ```
3. **`POST /jobs` 엔드포인트 작성**:
   * 상태 코드: `201 Created` (`status_code=201`)
   * 응답 모델: `response_model=JobResponse`
   * 요청 본문으로 `job_req: JobCreateRequest` 받기
   * 고유 ID 생성: `new_id = f"job-{uuid.uuid4().hex[:8]}"`
   * `JobResponse` 객체(또는 딕셔너리)를 반환:
     - `job_id`: 생성된 `new_id`
     - `task_type`: `job_req.task_type`
     - `target_file`: `job_req.target_file`
     - `priority`: `job_req.priority`
     - `status`: `JobStatus.PENDING`
     - `message`: `"Job submitted successfully"`

---

### [Step 2-3] Swagger UI(`/docs`)에서 직접 검증해보기

1. 서버가 실행 중인지 확인합니다 (실행 안 되어 있다면 터미널에서 `uvicorn app.api.main:app --reload`).
2. 브라우저에서 **`http://127.0.0.1:8000/docs`** 로 접속합니다.
3. 새로 생긴 **`POST /jobs`** 를 열고 `Try it out` 클릭!
4. **정상 요청 테스트**:
   * Request body에 아래 JSON을 넣고 `Execute`:
     ```json
     {
       "task_type": "resize",
       "target_file": "sample.jpg",
       "priority": 3
     }
     ```
   * ➡️ **`201` 코드와 함께 `job_id`가 채워진 응답이 오는지 확인**!
5. **Pydantic의 강력한 자동 검증 테스트 (일부러 에러 내보기)**:
   * `priority`에 `10`을 넣거나, `task_type`에 `"invalid_task"`를 넣고 `Execute`:
   * ➡️ FastAPI가 `422 Unprocessable Entity` 에러와 함께 어느 필드가 왜 틀렸는지 친절한 JSON 오류를 뱉어내는 것을 확인해 보세요!

---

## 4️⃣ 완료 및 체크 요청
두 가지 테스트(정상 201 응답, 비정상 422 응답)를 확인하셨다면 **"미션 2 다 했어, 체크해줘!"**라고 말씀해 주세요!
