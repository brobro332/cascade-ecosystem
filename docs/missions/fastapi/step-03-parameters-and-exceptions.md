# 🎯 [FastAPI Mission 03] 경로/쿼리 파라미터 & HTTPException 예외 처리

> **난이도**: ★★☆☆☆ (기초~중급)  
> **연계 CKA 개념**: `kubectl get pod <name>`의 404 NotFound 및 라벨 셀렉터(`--selector status=running`) 필터링 원리  
> **작업 대상 파일**: `app/api/main.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

* **경로 매개변수(Path Parameter) vs 쿼리 매개변수(Query Parameter)**
  * **경로 매개변수 (`/jobs/{job_id}`)**: 특정 자원 딱 하나를 콕 집어서 조회할 때 URL 경로 자체에 식별자를 포함합니다.
    * 예: `GET /jobs/job-a1b2c3d4` ➡️ "이 ID를 가진 작업 정보 줘!" (K8s의 `kubectl get pod my-pod`와 동일)
  * **쿼리 매개변수 (`/jobs?status=pending&limit=5`)**: 목록을 조회할 때 필터링, 정렬, 페이징 옵션을 URL 뒤에 `?key=value` 형태로 붙입니다.
    * 예: `GET /jobs?status=pending` ➡️ "대기 중인 작업들만 보여줘!" (K8s의 `kubectl get pods -l app=pipeline`과 동일)
* **왜 `HTTPException`을 발생시켜야 하나요?**
  * 없는 `job_id`를 조회했을 때 서버가 멈추거나 엉뚱하게 `200 OK`에 `null`을 주면 클라이언트는 혼란에 빠집니다.
  * REST API 표준 규약에 맞게 **"자원을 찾을 수 없음"을 나타내는 명확한 `404 Not Found` 에러**와 에러 메시지(`detail="Job not found"`)를 반환해야 합니다.

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  * **`자습서` → `경로 매개변수 (Path Parameters)`**: URL 경로에서 변수 추출하기 (`@app.get("/items/{item_id}")`)
  * **`자습서` → `쿼리 매개변수 (Query Parameters)`**: 기본값 설정 및 선택적(Optional) 매개변수 선언법
  * **`자습서` → `오류 처리 (Handling Errors)`**: `from fastapi import HTTPException` 및 `raise HTTPException(status_code=404, detail="...")` 사용법
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi 경로 매개변수 path parameter"`
  * `"fastapi query parameter 기본값 optional"`
  * `"fastapi httpexception 404 예외 처리"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 3-1] `app/api/main.py`에 임시 인메모리 저장소 추가 & POST 연동
아직 데이터베이스나 Redis를 연결하기 전이므로, 파이썬 딕셔너리로 서버 메모리에 작업을 보관합니다:

1. `app/api/main.py` 상단에 `HTTPException` 및 `Query` import 추가:
   ```python
   from fastapi import FastAPI, HTTPException, Query
   ```
2. 작업들을 저장할 딕셔너리 생성 (전역 변수):
   ```python
   # 임시 인메모리 저장소: {job_id: JobResponse}
   jobs_db: dict[str, JobResponse] = {}
   ```
3. 기존 **`POST /jobs`** 함수 내부에서 응답 객체를 만든 뒤 `jobs_db`에 저장하도록 1줄 추가:
   ```python
   jobs_db[new_id] = response
   ```

---

### [Step 3-2] 단일 작업 조회 API (`GET /jobs/{job_id}`) 구현

경로 매개변수로 `job_id`를 받아 해당 작업을 조회하고, 없으면 404를 던집니다:

1. 엔드포인트 선언:
   ```python
   @app.get("/jobs/{job_id}", response_model=JobResponse)
   def get_job(job_id: str):
   ```
2. 조회 로직:
   * `if job_id not in jobs_db:`
     * `raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")`
   * 존재하면 `return jobs_db[job_id]`

---

### [Step 3-3] 작업 목록 조회 & 필터링 API (`GET /jobs`) 구현

쿼리 매개변수로 상태 필터(`status`)와 조회 개수 제한(`limit`)을 받아 목록을 반환합니다:

1. 엔드포인트 선언 (반환 타입: `list[JobResponse]`):
   ```python
   @app.get("/jobs", response_model=list[JobResponse])
   def list_jobs(
       status: JobStatus | None = None,
       limit: int = Query(default=10, ge=1, le=50, description="최대 조회 개수 (1~50)")
   ):
   ```
2. 목록 필터링 로직:
   * `jobs = list(jobs_db.values())`
   * 만약 `status`가 주어졌다면 (`if status is not None:`): 해당 상태인 작업만 필터링
   * `limit` 개수만큼 슬라이싱하여 반환 (`return filtered_jobs[:limit]`)

---

### [Step 3-4] Swagger UI(`/docs`)에서 직접 검증해보기

1. 브라우저에서 **`http://127.0.0.1:8000/docs`** 로 접속합니다.
2. **`POST /jobs`** 로 작업 2개를 등록해 봅니다 (예: 하나는 `resize`, 하나는 `summary`).
   * 반환된 `job_id`를 복사해 둡니다.
3. **`GET /jobs/{job_id}` 단일 조회 테스트**:
   * 복사한 정상 `job_id` 입력 후 실행 ➡️ **`200 OK`와 해당 작업 데이터 반환 확인**
   * 존재하지 않는 임의의 ID(`job-fake-999`) 입력 후 실행 ➡️ **`404 Not Found` 및 detail 메시지 확인!**
4. **`GET /jobs` 목록 & 쿼리 필터링 테스트**:
   * 아무 조건 없이 실행 ➡️ 전체 작업 목록 확인
   * `status`에 `pending` 선택 후 실행 ➡️ 필터링된 결과 확인
   * `limit`에 `100` 입력 후 실행 ➡️ `422 Unprocessable Entity` (Pydantic Query `le=50` 제한 검증 확인!)

---

## 4️⃣ 완료 및 체크 요청
위 테스트들을 모두 확인하셨다면 **"미션 3 다 했어, 체크해줘!"**라고 말씀해 주세요!
