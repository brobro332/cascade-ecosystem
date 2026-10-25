# 🚀 FastAPI 실전 학습 진행 상황판 (`FASTAPI_PROGRESS.md`)

> **문서 목적 (Living Tracker)**:
> 에이전트가 매 스텝마다 확인하고 업데이트하는 **FastAPI 진행 대시보드 & 코드 리뷰/오답 노트**입니다.
> 각 스텝의 상세 실습 가이드는 **`docs/missions/fastapi/`** 폴더 아래에 개별 문서로 생성됩니다.
> **진행 원칙**: **무조건 로컬(현재 Windows 개발 PC) 우선!** 로컬에서 100% 실행·테스트하며 기초부터 다진 후, 로컬 K8s → 라즈베리파이 순으로 확장합니다.

---

## 📊 전체 진행 방향 및 미션 목록 (Local-First Curriculum)

| 단계 | 주제 | 핵심 학습 키워드 | 미션 가이드 문서 | 상태 |
| :--- | :--- | :--- | :--- | :---: |
| **Step 1** | **환경 세팅 & 첫 서버 구동 (Health Probe)** | `venv`, `uvicorn`, `@app.get`, `/healthz` | [`step-01-setup-and-healthz.md`](./missions/fastapi/step-01-setup-and-healthz.md) | ✅ **완료** |
| **Step 2** | **Pydantic v2 데이터 검증 & 스키마 설계** | `BaseModel`, `Field`, `Enum`, Request/Response | [`step-02-pydantic-validation.md`](./missions/fastapi/step-02-pydantic-validation.md) | ✅ **완료** |
| **Step 3** | **경로/쿼리 파라미터 & 예외 처리** | `Path`, `Query`, `HTTPException`, Status Code | [`step-03-parameters-and-exceptions.md`](./missions/fastapi/step-03-parameters-and-exceptions.md) | ✅ **완료** |
| **Step 4** | **`pytest`로 내 API 자동 테스트하기** | `TestClient`, `httpx.AsyncClient`, 단위 테스트 | [`step-04-pytest-testing.md`](./missions/fastapi/step-04-pytest-testing.md) | ✅ **완료** |
| **Step 5** | **비동기 원리 (`async def` vs `def`) & 파일 업로드** | 이벤트 루프 블로킹 원리, `UploadFile`, 로컬 저장 | [`step-05-async-and-file-upload.md`](./missions/fastapi/step-05-async-and-file-upload.md) | 🔄 **진행 중** |
| **Step 6** | **의존성 주입 (`Depends`) & 환경변수 (`pydantic-settings`)** | `Depends`, `BaseSettings`, 설정 분리 & Mocking | *(대기)* | ⏳ 대기 |
| **Step 7** | **Lifespan 관리 & 백그라운드 워커/큐 연동** | `@asynccontextmanager`, `BackgroundTasks` vs Redis | *(대기)* | ⏳ 대기 |
| **Step 8** | **공식 `kubernetes` Python Client 연동** | `BatchV1Api`로 K8s `Job` 동적 생성 (로컬 → 클러스터) | *(대기)* | ⏳ 대기 |

---

## 📌 현재 활성 미션 요약
* **현재 스텝**: **Step 5 — 비동기 원리 (`async def` vs `def`) & 실제 파일 업로드 구현**
* **가이드 위치**: [`docs/missions/fastapi/step-05-async-and-file-upload.md`](./missions/fastapi/step-05-async-and-file-upload.md)
* **체크 대상**:
  1. `python-multipart` 설치 및 `requirements.txt`, `.gitignore`(`storage/`) 반영 여부
  2. `app/api/main.py`에 `async def upload_job` (`POST /jobs/upload`) 구현 및 `await file.read()` 비동기 처리 확인
  3. 빈 파일(0바이트) 업로드 시 `400 Bad Request` 예외 처리 및 `storage/uploads/` 로컬 저장 동작 확인
  4. `tests/test_api.py`에 업로드 성공(201) 및 빈 파일 거부(400) 테스트 추가 후 `pytest -v` (`7 passed`) 통과 여부

---

## 📝 학습 히스토리 & 코드 리뷰 노트 (Agent Updated)
* **2026-10-25 (Step 4 완료)**:
  * `.venv` 내 `pytest`, `httpx`, `httpx2` 설치 및 `requirements.txt` 반영 확인.
  * `pytest.ini` (`pythonpath = .`) 설정으로 어디서든 `pytest -v`가 깔끔하게 동작하도록 구성 완료.
  * `tests/test_api.py`에 `@pytest.fixture(autouse=True)` 기반 `clear_jobs_db` 초기화 및 5대 핵심 시나리오 테스트 작성 완료 (`5 passed in 0.45s`).
  * 이전 Step 3 리뷰에서 언급했던 `app/api/main.py` 29번 줄 끝 세미콜론(`;`)까지 깔끔하게 정리됨!
  * Step 5 가이드([`step-05-async-and-file-upload.md`](./missions/fastapi/step-05-async-and-file-upload.md)) 오픈.
* **2026-10-25 (Step 3 완료)**:
  * `app/api/main.py`에 인메모리 저장소(`jobs_db: dict[str, JobResponse] = {}`) 연동 및 `POST /jobs` 저장 로직 구현 완료.
  * `GET /jobs/{job_id}`에서 미존재 ID 조회 시 `HTTPException(status_code=404, detail=...)` 반환 검증 완료.
  * `GET /jobs`에서 `status: JobStatus | None = None` 선택적 필터링(리스트 컴프리헨션 활용) 및 `Query(default=10, ge=1, le=50)` 슬라이싱 검증 100% 통과.
* **2026-10-25 (Step 2 완료)**:
  * `app/api/schemas.py`에 `TaskType(str, Enum)`, `JobStatus(str, Enum)`, `JobCreateRequest(BaseModel)`, `JobResponse(BaseModel)` 설계 완료.
  * `app/api/main.py`에 `POST /jobs` 엔드포인트 구현 (상태코드 `201 Created` 및 `JobResponse` 반환 타입 힌트 활용).
* **2026-10-23 (Step 1 완료)**:
  * `.venv` 가상환경 구축 및 기본 루트 엔드포인트(`GET /`)와 헬스 체크 엔드포인트(`GET /healthz`) 구현 통과.
