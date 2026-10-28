# 🚀 FastAPI 실전 학습 진행 상황판 & 해설집 (`FASTAPI_PROGRESS.md`)

> **문서 목적 (Living Tracker & Study Book)**:
> 이 문서는 FastAPI 트랙(Step 1~8)의 진행 대시보드이자, **각 스텝에서 우리가 무엇을 왜 배웠는지 언제든 다시 꺼내 볼 수 있는 '미션별 완료 해설집'**입니다.
> 각 스텝의 상세 실습 가이드는 **`docs/missions/fastapi/`** 폴더 아래에 있습니다.

---

## 📊 전체 진행 방향 및 미션 목록 (Local-First Curriculum) — 🎉 전 과정 완주!

| 단계 | 주제 | 핵심 학습 키워드 | 미션 가이드 문서 | 상태 |
| :--- | :--- | :--- | :--- | :---: |
| **Step 1** | **환경 세팅 & 첫 서버 구동 (Health Probe)** | `venv`, `uvicorn`, `@app.get`, `/healthz` | [`step-01-setup-and-healthz.md`](./missions/fastapi/step-01-setup-and-healthz.md) | ✅ **완료** |
| **Step 2** | **Pydantic v2 데이터 검증 & 스키마 설계** | `BaseModel`, `Field`, `Enum`, Request/Response | [`step-02-pydantic-validation.md`](./missions/fastapi/step-02-pydantic-validation.md) | ✅ **완료** |
| **Step 3** | **경로/쿼리 파라미터 & 예외 처리** | `Path`, `Query`, `HTTPException`, Status Code | [`step-03-parameters-and-exceptions.md`](./missions/fastapi/step-03-parameters-and-exceptions.md) | ✅ **완료** |
| **Step 4** | **`pytest`로 내 API 자동 테스트하기** | `TestClient`, `fixture`, `assert`, 단위 테스트 | [`step-04-pytest-testing.md`](./missions/fastapi/step-04-pytest-testing.md) | ✅ **완료** |
| **Step 5** | **비동기 원리 (`async def` vs `def`) & 파일 업로드** | 이벤트 루프 블로킹 원리, `UploadFile`, 로컬 저장 | [`step-05-async-and-file-upload.md`](./missions/fastapi/step-05-async-and-file-upload.md) | ✅ **완료** |
| **Step 6** | **의존성 주입 (`Depends`) & 환경변수 (`pydantic-settings`)** | `Depends`, `BaseSettings`, 설정 분리 & Mocking | [`step-06-depends-and-settings.md`](./missions/fastapi/step-06-depends-and-settings.md) | ✅ **완료** |
| **Step 7** | **Lifespan 관리 & 백그라운드 워커 연동** | `@asynccontextmanager`, `/readyz`, `BackgroundTasks` | [`step-07-lifespan-and-background-worker.md`](./missions/fastapi/step-07-lifespan-and-background-worker.md) | ✅ **완료** |
| **Step 8** | **공식 `kubernetes` Python Client 연동** | `BatchV1Api`로 K8s `Job` 동적 생성 (Mock 검증) | [`step-08-kubernetes-client.md`](./missions/fastapi/step-08-kubernetes-client.md) | ✅ **완료** |

---

## 📚 미션별 완료 해설집 (Step 1~8 핵심 요약 & 복습 노트)

### 📘 [Step 1 해설] 가상환경(`.venv`)과 `/healthz` 엔드포인트
* **내가 한 일**: 프로젝트 전용 파이썬 도구함(`.venv`)을 만들고, `uvicorn` 웹 서버로 `GET /`와 `GET /healthz`를 띄웠습니다.
* **핵심 포인트**: 쿠버네티스는 파드가 살아있는지 확인할 때 `/healthz`(Liveness Probe)를 찔러보고 `200 OK`가 나오는지 검사합니다.

### 📘 [Step 2 해설] Pydantic v2 스키마 검증 (`app/api/schemas.py`)
* **내가 한 일**: 손님이 아무 데이터나 막 보내지 못하도록 `TaskType`(`resize`, `watermark`, `summary`), `priority`(`1~5` 숫자 제한) 같은 **엄격한 주문서 양식(`JobCreateRequest`)**을 만들었습니다.
* **핵심 포인트**: 양식에 어긋난 요청(예: `priority: 99`)이 들어오면 내 코드가 실행되기도 전에 FastAPI가 자동으로 **`422 Unprocessable Entity`** 에러를 뱉어 막아줍니다!

### 📘 [Step 3 해설] 경로 매개변수 vs 쿼리 매개변수 & `404` 예외 처리
* **내가 한 일**:
  * **경로 매개변수 (`GET /jobs/{job_id}`)**: 딱 1개의 작업을 콕 집어 조회하고, 없으면 `HTTPException(status_code=404)`를 던졌습니다.
  * **쿼리 매개변수 (`GET /jobs?status=pending&limit=10`)**: 전체 목록에서 조건에 맞는 것만 골라내는 필터링 기능을 만들었습니다.

### 📘 [Step 4 해설] `pytest`와 `TestClient`로 0.5초 만에 자동 채점하기 (`tests/test_api.py`)
* **내가 한 일**: 매번 브라우저(`/docs`)에서 손으로 클릭하며 테스트하는 대신, 가짜 손님(`TestClient`)이 내 API들을 자동으로 호출하고 `assert`로 정답을 검사하는 테스트 코드를 짰습니다.
* **오답 주의점**: `assert response.status_code == 400`에서 앞에 `assert`를 빼먹으면 틀려도 그냥 통과해버리는 가짜 통과(False-Positive)가 되므로 반드시 `assert`를 적어야 합니다!

### 📘 [Step 5 해설] `async def` vs `def` 비동기 원리와 파일 업로드 (`UploadFile`)
* **내가 한 일**: `POST /jobs/upload`에서 진짜 이미지/문서 파일을 받아 `storage/uploads/` 폴더에 저장했습니다.
* **핵심 포인트**: 내부에서 `await file.read()`처럼 비동기 대기를 사용할 때는 **`async def`**를 쓰고, 일반 동기 함수를 쓸 때는 **`def`**를 써야 전체 서버(웨이터)가 멈추지 않습니다.

### 📘 [Step 6 해설] `BaseSettings` 환경변수와 `Depends` 갈아끼우기 (`app/api/config.py`)
* **내가 한 일**: 코드 안에 고정되어 있던 폴더 경로(`storage/uploads`)와 노드 이름을 `Settings(BaseSettings)`로 분리하고, 엔드포인트 매개변수에 `settings: Settings = Depends(get_settings)`로 꽂아주었습니다.
* **핵심 Q&A 요약**:
  * **`BaseSettings`를 쓰는 이유**: 나중에 쿠버네티스 `ConfigMap`으로 환경변수(`NODE_NAME=k8s-local-cluster`)를 주면 파이썬 코드 수정 없이 자동으로 값을 읽어오기 위해서!
  * **`Depends`를 쓰는 이유**: 여러 API에서 공통 부품을 편하게 꽂아 쓰고, 테스트할 땐 `app.dependency_overrides`로 **가짜(Mock) 부품으로 갈아끼우기 위해서!** (주의: 함수 몸통 안이 아니라 반드시 **함수 매개변수 괄호 `()` 안**에 적어야 동작함!)

### 📘 [Step 7 해설] `lifespan`(`GET /readyz`)과 `BackgroundTasks` 백그라운드 워커 (`app/worker/processor.py`)
* **내가 한 일**:
  * 손님이 작업을 등록하면 먼저 0.01초 만에 `"접수 완료(pending)"` 응답을 돌려주고, 손님이 간 직후 뒷방(`BackgroundTasks`)에서 워커가 돌아가며 상태를 `"완료(completed)"`로 바꾸게 만들었습니다.
  * 서버가 켜질 때 준비 완료 팻말(`app.state.is_ready = True`)을 걸어두는 `lifespan`과 쿠버네티스 Readiness Probe용 `/readyz`를 만들었습니다.

### 📘 [Step 8 해설] 공식 `kubernetes` 클라이언트로 외주 작업(`V1Job`) 보내기 (`app/api/k8s_client.py`)
* **내가 한 일**: 무거운 작업이 들어오면 FastAPI가 직접 일하지 않고, 쿠버네티스에게 **"일회용 작업 파드(`Job`) 하나 띄워서 대신 처리해 줘!"**라고 보낼 외주 주문서(`V1Job`)를 조립하고 전송(`K8sJobDispatcher`)하는 `POST /jobs/k8s`를 만들었습니다.
* **핵심 Q&A 요약 (`try/except` 예외 처리 vs `Depends` Mock 테스트)**:
  * **`try / except` (자동차 에어백)**: 실제 운영 중 쿠버네티스가 죽었을 때 서버가 안 꺼지고 `503 에러`를 안내하는 방어막.
  * **`Depends` (운전면허 시뮬레이터)**: 내 노트북에 쿠버네티스가 안 깔려 있을 때도 가짜 전화기(`FakeK8sDispatcher`)를 꽂아서 **내가 만든 외주 주문서(`V1Job`)가 오타 없이 잘 조립되는지 `201 성공` 시나리오를 테스트(Mocking)**하는 도구!
