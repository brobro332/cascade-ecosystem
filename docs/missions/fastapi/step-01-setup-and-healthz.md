# 🎯 [FastAPI Mission 01] 가상환경 세팅 & 첫 서버 띄우기 (`/healthz`)

> **난이도**: ★☆☆☆☆ (입문)
> **연계 CKA 개념**: Liveness Probe (`/healthz` 상태 체크 엔드포인트)
> **작업 대상 파일**: `requirements.txt`, `app/api/main.py`

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

* **왜 가상환경(`.venv`)부터 만드나요?**
  내 윈도우 PC 전체에 파이썬 패키지를 그냥 설치하면, 나중에 다른 프로젝트와 버전이 꼬여서 고장 납니다. 이 프로젝트 폴더(`cascade-ecosystem`) 안에서만 독립적으로 쓰는 **"전용 공구함(`.venv`)"**을 만드는 과정입니다.
* **FastAPI와 `uvicorn`은 무슨 관계인가요?**
  * **FastAPI**: 손님(브라우저/쿠버네티스)이 어떤 주소(`/healthz`)로 찾아오면 어떤 요리(JSON 응답)를 내어줄지 적힌 **'주방 레시피(파이썬 코드)'**입니다.
  * **Uvicorn**: 실제로 가게 문을 열고 포트(`8000`번)에서 손님을 맞이해 FastAPI에게 주문을 전달하는 **'초고속 웹 서버(웨이터)'**입니다.
* **왜 첫 엔드포인트로 `/healthz`를 만드나요?**
  나중에 쿠버네티스(CKA)에 이 서버를 올리면, 쿠버네티스가 10초마다 `/healthz` 주소로 노크해서 **"너 안 죽고 살아있니?(Liveness Probe)"**라고 확인합니다. 이때 `{"status": "ok"}`와 함께 `200 OK`를 돌려주지 않으면 쿠버네티스가 파드를 강제로 재시작시켜 버립니다!

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

코드 작성 전 딱 5분만 아래 문서를 눈으로 훑어보세요!

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  * 이동 경로: **`자습서 - 사용자 가이드 (Tutorial - User Guide)` → `첫 걸음 (First Steps)`**
  * **집중해서 볼 포인트 3가지**:
    1. `from fastapi import FastAPI` 후 `app = FastAPI()` 인스턴스를 어떻게 생성하는지
    2. `@app.get("/")` 데코레이터 아래에 함수를 어떻게 정의하고 파이썬 딕셔너리(`{"키": "값"}`)를 `return` 하는지
    3. 서버를 띄운 뒤 `/docs` 주소로 들어가면 무엇이 나오는지
* **🔎 막힐 때 구글 검색 키워드**:
  * `"python venv 가상환경 생성 windows powershell"`
  * `"powershell ExecutionPolicy RemoteSigned 가상환경 활성화 오류"`
  * `"fastapi uvicorn 실행 방법"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

VS Code 터미널(PowerShell)을 열고 프로젝트 루트(`c:\Users\332br\workspace\cascade-ecosystem`)에서 아래 순서대로 직접 진행해 보세요.

### [Step 1-1] 파이썬 가상환경 만들고 켜기
1. 가상환경 생성:
   ```powershell
   python -m venv .venv
   ```
2. 가상환경 활성화 (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(💡 팁: 만약 윈도우 보안 정책 때문에 빨간 글씨 오류가 나면 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 를 한 번 친 뒤 다시 실행하세요)*
3. 터미널 입력줄 맨 앞에 `(.venv)` 초록색 표시가 붙었는지 확인합니다.

### [Step 1-2] 필수 패키지 설치 및 `requirements.txt` 작성
1. 패키지 설치:
   ```powershell
   pip install "fastapi[standard]" pytest httpx
   ```
2. 프로젝트 루트(`cascade-ecosystem/requirements.txt`)에 파일을 직접 만들고 아래 3줄을 적어 저장합니다:
   ```text
   fastapi[standard]
   pytest
   httpx
   ```

### [Step 1-3] 첫 번째 API 작성 (`app/api/main.py`)
`app/api/main.py` 파일을 직접 생성하고, 공식 문서의 **'첫 걸음(First Steps)'** 예제를 참고해 아래 2개의 GET 엔드포인트를 만들어 보세요:
1. **`GET /`** 요청 시 반환할 JSON:
   ```json
   {"service": "kube-pipeline-api", "message": "Hello CKA & FastAPI!"}
   ```
2. **`GET /healthz`** 요청 시 반환할 JSON:
   ```json
   {"status": "ok"}
   ```

### [Step 1-4] 내 손으로 서버 띄워서 확인하기
1. 터미널에서 서버 실행:
   ```powershell
   uvicorn app.api.main:app --reload
   ```
2. 브라우저를 열고 아래 주소들을 직접 들어가 보세요:
   * `http://127.0.0.1:8000/`
   * `http://127.0.0.1:8000/healthz`
   * `http://127.0.0.1:8000/docs` (Swagger UI에서 `Try it out` → `Execute` 버튼도 눌러보세요!)

---

## 4️⃣ 완료 및 체크 요청
여기까지 해보시고 잘 뜨면 에이전트에게 **"미션 1 다 했어, 체크해줘!"**라고 말씀해 주세요!
(중간에 에러가 나거나 궁금한 게 있으면 언제든 물어보세요!)
