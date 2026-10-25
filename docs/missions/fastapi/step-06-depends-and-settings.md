# 🎯 [FastAPI Mission 06] 의존성 주입 (`Depends`) & 환경변수 설정 (`pydantic-settings`)

> **난이도**: ★★★☆☆ (중급 — FastAPI 아키텍처의 꽃!)  
> **연계 CKA 개념**: 쿠버네티스 `ConfigMap` / `Secret` 환경변수 주입 및 Downward API (`NODE_NAME` 주입)  
> **작업 대상 파일**: `requirements.txt`, `app/api/config.py` (신규), `app/api/main.py`, `tests/test_api.py`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. 왜 코드에 경로(`"storage/uploads"`)를 직접 적으면(하드코딩) 안 될까요?
지금 `app/api/main.py` 상단에는 `UPLOAD_DIR = Path("storage/uploads")`라고 고정되어 있습니다.  
하지만 실무와 쿠버네티스(CKA) 환경에서는 실행되는 곳마다 설정이 달라집니다:
* **내 윈도우 노트북 (로컬 개발)**: `storage/uploads` 폴더에 저장
* **자동 테스트 (`pytest` 실행 시)**: 실제 폴더를 더럽히지 않게 임시 폴더(`tmp_path`)에 저장
* **쿠버네티스 클러스터 (라즈베리파이/노트북 워커)**: 공유 볼륨(PVC)이 마운트된 `/mnt/pipeline-data/uploads`에 저장

이때 코드를 매번 고쳐서 이미지를 다시 빌드할 수는 없겠죠?  
그래서 쿠버네티스의 **`ConfigMap`**으로 환경변수(`UPLOAD_DIR=/mnt/pipeline-data/uploads`, `NODE_NAME=k8s-worker-1`)를 찔러 넣어주면, 파이썬 앱이 환경변수를 자동으로 읽어 적용하게 만드는 도구가 바로 **`pydantic-settings` (`BaseSettings`)**입니다!

---

### 💡 2. `Depends` (의존성 주입, Dependency Injection)란?
* **쉬운 비유**: 요리사(엔드포인트 함수 `upload_job`)가 요리할 때마다 직접 마트에 가서 식재료(설정 객체, DB 연결, K8s 클라이언트)를 사 오는 게 아니라, **"나 `Settings` 필요해(`Depends(get_settings)`)!"**라고 주문서만 적어두면 FastAPI가 알아서 준비해 손에 쥐여주는 시스템입니다.
* **가장 강력한 무기 (`dependency_overrides`)**:
  * 평소에는 진짜 설정(`get_settings`)을 쥐여주다가,
  * `pytest`로 테스트할 때만 **`app.dependency_overrides[get_settings] = 가짜_설정_함수`** 딱 한 줄로 요리사 몰래 재료를 바꿔치기(Mocking)할 수 있습니다!

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 FastAPI 공식 한글 문서 (`https://fastapi.tiangolo.com/ko/`)**:
  1. **`자습서 - 사용자 가이드` → `의존성 (Dependencies)` → `첫 걸음 (First Steps)`**:
     * `from fastapi import Depends`를 함수 매개변수에 어떻게 쓰는지 확인
  2. **`고급 사용자 가이드 (Advanced User Guide)` → `설정 및 환경 변수 (Settings and Environment Variables)`**:
     * `from pydantic_settings import BaseSettings`로 환경변수를 자동으로 읽는 클래스 만드는 법
  3. **`자습서 - 사용자 가이드` → `테스팅: 의존성 오버라이드 (Testing Dependencies with Overrides)`**:
     * 테스트 코드에서 `app.dependency_overrides`로 의존성을 바꿔치기하는 예제 확인!
* **🔎 막힐 때 구글 검색 키워드**:
  * `"fastapi pydantic-settings BaseSettings 사용법"`
  * `"fastapi Depends dependency_overrides pytest"`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 6-0] 지난 Step 5 테스트 코드의 숨은 함정 1줄 먼저 고치기! 🛠️
`tests/test_api.py`의 맨 마지막 줄(73번 줄)을 잠깐 보실까요?
```python
    response.status_code == 400
```
앞에 **`assert`**가 빠져 있어서, 만약 상태 코드가 400이 아니더라도 테스트가 무조건 통과해버리는 상태입니다!  
73번 줄 맨 앞에 **`assert response.status_code == 400`** 으로 `assert`를 꼭 붙여주세요!

---

### [Step 6-1] `pydantic-settings` 패키지 설치
Pydantic v2부터는 환경변수 관리 기능이 `pydantic-settings`라는 별도 패키지로 분리되었습니다.

1. 가상환경(`(.venv)`) 터미널에서 설치:
   ```powershell
   pip install pydantic-settings
   ```
2. `requirements.txt` 마지막 줄에 `pydantic-settings`를 추가해 주세요.

---

### [Step 6-2] 설정 파일 `app/api/config.py` 새로 만들기

`app/api/config.py` 파일을 생성하고 아래 구조로 `Settings` 클래스와 `get_settings()` 함수를 작성해 보세요:

1. 필요한 모듈 import:
   ```python
   from pathlib import Path
   from pydantic_settings import BaseSettings
   ```
2. `Settings(BaseSettings)` 클래스 정의 (환경변수 이름과 대소문자 무관하게 자동 매칭됩니다!):
   * `app_name: str = "kube-pipeline-api"`
   * `upload_dir: Path = Path("storage/uploads")`
   * `node_name: str = "local-dev-node"`  
     *(나중에 쿠버네티스 파드로 띄울 때 K8s가 `NODE_NAME` 환경변수에 `k8s-control-plane`(라즈베리파이) 또는 `k8s-worker-1`(노트북)을 자동으로 넣어줄 자리입니다!)*
3. 의존성 주입용 함수 `get_settings()` 정의:
   ```python
   def get_settings() -> Settings:
       return Settings()
   ```

---

### [Step 6-3] `app/api/main.py`에서 하드코딩 제거 & `Depends` 적용

1. `app/api/main.py` 상단에 `Depends`와 `Settings`, `get_settings`를 import 합니다:
   ```python
   from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Depends
   from app.api.config import Settings, get_settings
   ```
2. 기존에 전역 변수로 있던 `UPLOAD_DIR = Path("storage/uploads")` 줄을 **삭제**합니다 (또는 주석 처리).
3. **`GET /` (`read_root`) 수정**:
   * 매개변수에 `settings: Settings = Depends(get_settings)`를 추가합니다.
   * 반환 딕셔너리에 `"node_name": settings.node_name`을 추가해 보세요:
     ```python
     return {
         "service": settings.app_name,
         "node_name": settings.node_name,
         "message": "Hello CKA & FastAPI!"
     }
     ```
4. **`POST /jobs/upload` (`upload_job`) 수정**:
   * 매개변수 끝에 `settings: Settings = Depends(get_settings)`를 추가합니다.
   * 함수 안에서 기존 `UPLOAD_DIR` 대신 **`settings.upload_dir`**를 사용하도록 바꿉니다 (`settings.upload_dir.mkdir(...)`, `settings.upload_dir / file.filename`).

---

### [Step 6-4] `tests/test_api.py`에서 `dependency_overrides` 테스트 추가하기!

`tests/test_api.py` 맨 아래에 **실제 `storage/uploads` 폴더를 전혀 건드리지 않고, pytest가 제공하는 임시 폴더(`tmp_path`)와 가짜 노드 이름으로 바꿔치기하는 테스트**를 추가해 보세요:

1. 상단에 `from app.api.config import Settings, get_settings` 추가
2. 맨 아래에 테스트 함수 작성:
   ```python
   def test_settings_override(tmp_path: Path):
       # 1. 가짜 설정을 반환하는 함수 정의 (업로드 경로를 임시 폴더 tmp_path로 변경!)
       def get_test_settings() -> Settings:
           return Settings(upload_dir=tmp_path, node_name="k8s-worker-laptop")

       # 2. FastAPI 의존성 바꿔치기 (Override)
       app.dependency_overrides[get_settings] = get_test_settings

       try:
           # 루트 조회 시 바뀐 node_name이 나오는지 확인
           root_res = client.get("/")
           assert root_res.status_code == 200
           assert root_res.json()["node_name"] == "k8s-worker-laptop"

           # 파일 업로드 시 storage/uploads가 아니라 tmp_path에 저장되는지 확인!
           up_res = client.post(
               "/jobs/upload",
               files={"file": ("override_test.txt", b"hello-k8s", "text/plain")},
           )
           assert up_res.status_code == 201
           assert (tmp_path / "override_test.txt").exists()
       finally:
           # 3. 다른 테스트에 영향을 주지 않도록 반드시 초기화!
           app.dependency_overrides.clear()
   ```
3. 터미널에서 `pytest -v`를 실행해 **`8 passed`**가 뜨는지 확인해 보세요!

---

## 4️⃣ 완료 및 체크 요청
`8 passed`를 확인하셨다면 **"미션 6 다 했어, 체크해줘!"**라고 말씀해 주세요!
