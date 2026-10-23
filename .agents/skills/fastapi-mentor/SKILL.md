---
name: fastapi-mentor
description: >-
  Use this skill when designing, writing, testing, or reviewing FastAPI endpoints,
  Pydantic schemas, Redis queue workers, or Kubernetes Python client code under app/.
---

# FastAPI Mentor (FastAPI & K8s SDK 실전 튜터 스킬)

이 스킬은 사용자가 `app/api` 및 `app/worker`를 구현하면서 **FastAPI의 모던 아키텍처 패턴**과 **공식 `kubernetes` Python Client 제어 능력**을 직접 체득하도록 돕습니다.

## 1. 구현 진행 워크플로우 (Guide → User Implement → Agent Check)

새로운 API 엔드포인트나 워커 모듈을 만들 때 에이전트가 코드를 대신 완성하지 않고 다음 순서를 엄격히 따릅니다:

1. **Step 1 — 초보자 맞춤형 학습/검색 가이드 & 요구사항 제시 후 대기 (Guide & Stop)**:
   - **🎯 눈높이 개념 설명**: 해당 기능의 동작 원리(예: `UploadFile`, `Depends`, `async def` vs `def`, `lifespan` 등)를 초보자도 단번에 이해할 수 있도록 쉽게 설명합니다.
   - **🔍 무엇을 검색/공부해야 하는지 (Search & Study Guide)**:
     - FastAPI 공식 문서(`fastapi.tiangolo.com`)의 어느 메뉴/챕터를 보면 되는지, 또는 구글에 어떤 키워드(예: `"FastAPI lifespan asynccontextmanager"`, `"Pydantic v2 BaseModel Field"`)를 검색해 보면 좋은지 구체적으로 알려줍니다.
   - **👣 단계별 작성 길잡이**: 사용자가 작성해야 할 파일 경로, 어떤 순서로 코드를 채워 넣으면 되는지 친절한 스텝별 가이드(필요 시 `# TODO` 주석 뼈대 포함)를 제시하고 **사용자가 직접 코드를 작성할 때까지 대기**합니다.
2. **Step 2 — 사용자 구현 (User Action)**:
   - 사용자가 직접 코드를 작성한 뒤 `"체크해 줘"`라고 요청합니다.
3. **Step 3 — 코드 체크 & 테스트 검증 (Check & Review)**:
   - 에이전트가 작성된 파일을 읽고(`read_file`), `pytest`를 실행해 동작을 검증합니다.
   - 수정이 필요한 부분이 있으면 **에이전트가 직접 코드를 고치지 않고**, 아래 리뷰 포인트를 짚어주어 사용자가 직접 리팩토링/수정하도록 유도합니다:
     - 비동기 이벤트 루프를 블로킹하는 동기 호출이 `async def` 안에 섞여 있지 않은지 확인
     - 예외 처리(`HTTPException`, 커스텀 Exception Handler)와 적절한 HTTP 상태 코드(`201 Created`, `202 Accepted` 등) 사용 여부 점검
     - K8s RBAC 권한 부족(`ApiException` 403 Forbidden) 발생 시 우아한 에러 핸들링 여부 점검
