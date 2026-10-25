# 🎯 [FastAPI Mission 04] `pytest`로 내 API 자동 테스트하기

> **난이도**: ★★☆☆☆ (기초~중급)  
> **연계 CKA / DevOps 개념**: 컨테이너 이미지(`docker build`) 배포 전 CI/CD 파이프라인의 자동 품질 게이트(Quality Gate) & Regression 검증  
> **작업 대상 파일**: `requirements.txt`, `tests/test_api.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

* **왜 Swagger UI(`/docs`)로 손으로 눌러보는 걸로 부족할까요?**
  * 지금은 API가 4개뿐이지만, 앞으로 파일 업로드·Redis 큐·쿠버네티스 Job 생성까지 붙으면 엔드포인트가 10개, 20개로 늘어납니다.
  * 코드를 한 줄 고칠 때마다 브라우저에서 20개 버튼을 일일이 손으로 눌러볼 수는 없겠죠?
  * **`pytest` + `TestClient`**를 쓰면 **서버(`uvicorn`)를 실제로 띄우지 않고도** 단 0.5초 만에 가짜 손님(TestClient)이 내 모든 API에 정상 요청·불량 요청을 쏴보고 상태 코드(`200`, `201`, `404`, `422`)가 맞는지 자동으로 채점해 줍니다!
* **`assert` 문법이란?**
  * 파이썬의 `assert 조건식`은 **"이 조건이 무조건 참(True)이어야 해! 아니면 테스트 실패(에러)를 내라!"**라는 뜻입니다.
  * 예: `assert response.status_code == 200` ➡️ 응답 코드가 200이면 통과(초록불 `PASSED`), 아니면 실패(빨간불 `FAILED`).

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

코드 작성 전 공식 문서의 **테스팅(Testing)** 챕터를 딱 5분만 읽어보세요!

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  * 이동 경로: **`자습서 - 사용자 가이드 (Tutorial - User Guide)` → `테스팅 (Testing)`**
  * **집중해서 볼 포인트 3가지**:
    1. `from fastapi.testclient import TestClient` 를 어떻게 가져오는지
    2. `client = TestClient(app)` 로 가짜 클라이언트를 어떻게 생성하는지
    3. `def test_...():` 함수 안에서 `client.get(...)`, `client.post(..., json={...})` 호출 후 `assert response.status_code == ...` 와 `assert response.json() == ...` 로 어떻게 검증하는지
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi TestClient pytest 사용법"`
  * `"pytest fixture autouse 초기화"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 4-1] `.venv`에 테스트 패키지 설치 확인하기
현재 최신 `starlette`/`fastapi`의 `TestClient`는 내부적으로 `httpx2` 패키지를 사용합니다.  
VS Code 터미널에서 가상환경(`(.venv)`)이 켜진 상태로 아래 명령어를 실행해 테스트 도구를 설치해 주세요:

```powershell
.\.venv\Scripts\Activate.ps1
pip install pytest httpx httpx2
```

그리고 `requirements.txt`에도 `httpx2`를 한 줄 추가해 주세요.

---

### [Step 4-2] `tests/test_api.py` 파일 생성 및 기본 준비

`tests/test_api.py` 파일을 새로 만들고 상단에 필요한 모듈과 `TestClient`를 선언합니다:

```python
import pytest
from fastapi.testclient import TestClient
from app.api.main import app, jobs_db

client = TestClient(app)

# 각 테스트 함수가 실행되기 전에 인메모리 저장소(jobs_db)를 깨끗이 비워주는 Fixture
@pytest.fixture(autouse=True)
def clear_jobs_db():
    jobs_db.clear()
```
*(💡 왜 `clear_jobs_db`가 필요한가요? 앞선 테스트에서 넣은 작업 데이터가 다음 테스트의 목록 개수에 영향을 주지 않도록 매 테스트마다 DB를 초기화하는 실무 필수 패턴입니다!)*

---

### [Step 4-3] 5가지 핵심 시나리오 테스트 함수 작성하기

`tests/test_api.py` 아래에 공식 문서의 예제를 참고하여 **`test_`로 시작하는 함수 5개**를 직접 작성해 보세요:

1. **`test_healthz()`**:
   * `GET /healthz` 호출
   * `status_code`가 `200`인지, `response.json()`이 `{"status": "ok"}`인지 `assert`로 검증
2. **`test_create_and_get_job()`**:
   * `POST /jobs`에 `json={"task_type": "resize", "target_file": "photo.png", "priority": 2}` 전송
   * 응답 `status_code`가 `201`인지 확인하고, 응답 JSON에서 `job_id`를 꺼냄
   * 꺼낸 `job_id`로 `GET /jobs/{job_id}`를 호출해 `status_code == 200` 및 `target_file == "photo.png"` 확인
3. **`test_get_nonexistent_job_returns_404()`**:
   * 없는 ID(예: `GET /jobs/job-ghost-999`) 호출 시 `status_code == 404`인지 검증
4. **`test_list_jobs_filter_and_limit()`**:
   * `POST /jobs`로 작업을 2개 이상 생성
   * `GET /jobs?status=pending` 호출 시 `len(response.json()) == 2` 확인
   * `GET /jobs?status=completed` 호출 시 `len(response.json()) == 0` 확인
   * `GET /jobs?limit=1` 호출 시 `len(response.json()) == 1` 확인
5. **`test_invalid_job_returns_422()`**:
   * 잘못된 요청(예: `priority: 99` 또는 `limit=100`)을 보냈을 때 FastAPI가 `status_code == 422`를 반환하는지 검증

---

### [Step 4-4] 터미널에서 `pytest` 실행해보기!

코드를 다 작성하셨다면 터미널에서 아래 명령어를 쳐보세요:

```powershell
pytest -v
```

초록색으로 **`5 passed`**가 뜨는지 확인해 보세요! (만약 `PYTHONPATH` 문제로 `ModuleNotFoundError: No module named 'app'`이 뜨면 **`python -m pytest -v`** 로 실행하면 현재 폴더를 자동으로 인식합니다!)

---

## 4️⃣ 완료 및 체크 요청
`5 passed` 화면을 확인하셨다면 **"미션 4 다 했어, 체크해줘!"**라고 말씀해 주세요!
