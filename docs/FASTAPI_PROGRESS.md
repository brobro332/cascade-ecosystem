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
| **Step 2** | **Pydantic v2 데이터 검증 & 스키마 설계** | `BaseModel`, `Field`, `Enum`, Request/Response | [`step-02-pydantic-validation.md`](./missions/fastapi/step-02-pydantic-validation.md) | 🔄 **진행 중** |
| **Step 3** | **경로/쿼리 파라미터 & 예외 처리** | `Path`, `Query`, `HTTPException`, Status Code | *(대기)* | ⏳ 대기 |
| **Step 4** | **`pytest`로 내 API 자동 테스트하기** | `TestClient`, `httpx.AsyncClient`, 단위 테스트 | *(대기)* | ⏳ 대기 |
| **Step 5** | **비동기 원리 (`async def` vs `def`) & 파일 업로드** | 이벤트 루프 블로킹 원리, `UploadFile`, 로컬 저장 | *(대기)* | ⏳ 대기 |
| **Step 6** | **의존성 주입 (`Depends`) & 환경변수 (`pydantic-settings`)** | `Depends`, `BaseSettings`, 설정 분리 & Mocking | *(대기)* | ⏳ 대기 |
| **Step 7** | **Lifespan 관리 & 백그라운드 워커/큐 연동** | `@asynccontextmanager`, `BackgroundTasks` vs Redis | *(대기)* | ⏳ 대기 |
| **Step 8** | **공식 `kubernetes` Python Client 연동** | `BatchV1Api`로 K8s `Job` 동적 생성 (로컬 → 클러스터) | *(대기)* | ⏳ 대기 |

---

## 📌 현재 활성 미션 요약
* **현재 스텝**: **Step 2 — Pydantic v2 데이터 검증 & 스키마 설계**
* **가이드 위치**: [`docs/missions/fastapi/step-02-pydantic-validation.md`](./missions/fastapi/step-02-pydantic-validation.md)
* **체크 대상**:
  1. `app/api/schemas.py` 신규 생성 (`TaskType`, `JobStatus`, `JobCreateRequest`, `JobResponse`)
  2. `app/api/main.py`에 `POST /jobs` 엔드포인트 구현 (상태코드 201, `response_model=JobResponse`)
  3. Swagger(`/docs`)에서 정상 요청(201) 및 유효성 검증 실패(422) 동작 확인

---

## 📝 학습 히스토리 & 코드 리뷰 노트 (Agent Updated)
* **2026-10-23 (Step 1 완료)**:
  * `.venv` 가상환경 구축 및 `fastapi[standard]`, `pytest`, `httpx` 설치 확인.
  * `app/api/main.py`에 기본 루트 엔드포인트(`GET /`)와 헬스 체크 엔드포인트(`GET /healthz`) 구현 및 자동 테스트 통과.
  * **💡 실전 코칭 포인트**: 윈도우 터미널 재실행 시 가상환경 활성화(`.\.venv\Scripts\Activate.ps1`) 필수 확인 습관화. 쿠버네티스 Liveness Probe 연동 시 `/healthz`가 200 OK를 반환해야 파드가 재시작(Restart loop)에 빠지지 않는다는 점 이해.
  * Step 2 가이드([`step-02-pydantic-validation.md`](./missions/fastapi/step-02-pydantic-validation.md)) 오픈 및 진행 시작.
