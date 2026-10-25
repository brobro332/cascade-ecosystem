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
| **Step 5** | **비동기 원리 (`async def` vs `def`) & 파일 업로드** | 이벤트 루프 블로킹 원리, `UploadFile`, 로컬 저장 | [`step-05-async-and-file-upload.md`](./missions/fastapi/step-05-async-and-file-upload.md) | ✅ **완료** |
| **Step 6** | **의존성 주입 (`Depends`) & 환경변수 (`pydantic-settings`)** | `Depends`, `BaseSettings`, 설정 분리 & Mocking | [`step-06-depends-and-settings.md`](./missions/fastapi/step-06-depends-and-settings.md) | ✅ **완료** |
| **Step 7** | **Lifespan 관리 & 백그라운드 워커/큐 연동** | `@asynccontextmanager`, `/readyz`, `BackgroundTasks` | [`step-07-lifespan-and-background-worker.md`](./missions/fastapi/step-07-lifespan-and-background-worker.md) | 🔄 **진행 중** |
| **Step 8** | **공식 `kubernetes` Python Client 연동** | `BatchV1Api`로 K8s `Job` 동적 생성 (로컬 → 클러스터) | *(대기)* | ⏳ 대기 |

---

## 📌 현재 활성 미션 요약
* **현재 스텝**: **Step 7 — Lifespan 관리 (`/readyz`) & 백그라운드 워커 (`BackgroundTasks`)**
* **가이드 위치**: [`docs/missions/fastapi/step-07-lifespan-and-background-worker.md`](./missions/fastapi/step-07-lifespan-and-background-worker.md)
* **체크 대상**:
  1. `app/worker/processor.py` 생성 및 `process_job_in_background` 구현 여부
  2. `app/api/main.py`에 `@asynccontextmanager` 기반 `lifespan` 및 `GET /readyz` 추가 여부
  3. `POST /jobs`, `POST /jobs/upload`에 `BackgroundTasks` 연동 여부
  4. `tests/test_api.py` 업데이트 및 `pytest -v` (`9 passed`) 통과 여부

---

## 📝 학습 히스토리 & 코드 리뷰 노트 (Agent Updated)
* **2026-10-25 (Step 6 완료)**:
  * `app/api/config.py`에 `Settings(BaseSettings)` 및 `get_settings()` 구현 완료.
  * `app/api/main.py`에서 함수 매개변수(`settings: Settings = Depends(get_settings)`)를 통한 의존성 주입 적용 완료.
  * `tests/test_api.py` 74번 줄 `assert response.status_code == 400` 보완 및 `app.dependency_overrides[get_settings]`를 활용한 임시 폴더(`tmp_path`) 오버라이드 테스트 통과 (`8 passed in 0.53s`).
  * **💡 오답/디버깅 노트**:
    * `Depends(...)`는 함수 몸통(Body) 안이 아니라 반드시 **엔드포인트 함수의 매개변수 괄호 안**에 선언해야 FastAPI가 호출 시점에 실제 객체로 주입해 줌을 직접 경험하며 체득!
  * Step 7 가이드([`step-07-lifespan-and-background-worker.md`](./missions/fastapi/step-07-lifespan-and-background-worker.md)) 오픈.
* **2026-10-25 (Step 5 완료)**:
  * `python-multipart` 설치 및 `POST /jobs/upload` (`async def`, `await file.read()`) 구현 완료.
* **2026-10-25 (Step 4 완료)**:
  * `pytest.ini` 및 `tests/test_api.py` 5대 시나리오 테스트 작성 완료.
* **2026-10-25 (Step 3 완료)**:
  * `GET /jobs/{job_id}` (404 예외 처리) 및 `GET /jobs` (`status`, `limit` 쿼리 필터링) 구현 완료.
* **2026-10-25 (Step 2 완료)**:
  * `app/api/schemas.py` Pydantic v2 모델 및 `POST /jobs` 구현 완료.
* **2026-10-23 (Step 1 완료)**:
  * `.venv` 가상환경 구축 및 `GET /`, `GET /healthz` 구현 통과.
