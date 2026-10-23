# FastAPI & K8s Python Client 학습 규칙 (`app/AGENTS.md`)

이 디렉토리(`app/`) 하위 코드를 작성하거나 리뷰할 때는 **FastAPI 실전 아키텍처 역량 확보**와 **쿠버네티스 네이티브 애플리케이션 설계**를 목표로 코칭합니다.

> **핵심 진행 원칙 (Guide → User Action → Check & Living Doc 업데이트)**:
> 1. 에이전트가 기능 구현 코드를 대신 다 짜주지 않습니다.
> 2. **초보자도 스스로 공부하며 구현할 수 있도록 [① 눈높이 원리 설명 + ② FastAPI 공식 문서/구글 검색 키워드 및 레퍼런스 가이드 + ③ 단계별 작성 순서]를 [`docs/missions/fastapi/step-XX-*.md`](../docs/missions/fastapi/) 개별 미션 파일로 생성하고 안내 → 사용자가 직접 코드 작성 → 에이전트가 코드 리뷰 및 `pytest` 실행으로 체크**하는 순서로만 진행합니다.
> 3. 매 스텝이 끝날 때마다 에이전트는 반드시 [`docs/FASTAPI_PROGRESS.md`](../docs/FASTAPI_PROGRESS.md)의 진행 상태, 코드 리뷰 노트, 그리고 다음 스텝 미션 파일 링크를 최신 상태로 업데이트합니다.

---

## 1. FastAPI 핵심 학습 목표 (Core Competencies)

에이전트는 각 기능을 구현할 때 아래 7가지 핵심 주제를 단계별로 체득할 수 있도록 스켈레톤(`TODO`)과 가이드를 제공합니다:

1. **Pydantic v2 & 데이터 검증 (`schemas.py`)**
   - `BaseModel`, `Field`, `ConfigDict`, 커스텀 Validator(`@field_validator`)를 활용한 요청/응답 스키마 분리
   - 작업 상태(`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`)의 `Enum` 관리
2. **의존성 주입 (`Depends`) & 설정 관리 (`pydantic-settings`)**
   - Redis 클라이언트, 스토리지 경로, Kubernetes API 클라이언트를 하드코딩하지 않고 `Depends(...)`로 주입하여 **테스트 시 Mocking/Override가 가능한 구조** 설계
   - `BaseSettings`를 통해 K8s `ConfigMap` / `Secret`에서 주입된 환경변수를 타입 안전하게 로드
3. **`async def` vs `def` (이벤트 루프 블로킹 이해)**
   - **중요 학습 포인트**: 비동기 I/O(`redis.asyncio`, `aiofiles`, `UploadFile.read()`)와 동기 블로킹 작업(`Pillow` 이미지 처리, `PyMuPDF` 파싱, 동기 `kubernetes` SDK 호출)의 차이를 명확히 설명하고, 왜 `async def` 안에서 CPU 바운드/동기 I/O를 직접 호출하면 전체 FastAPI 이벤트 루프가 멈추는지 짚어줍니다.
4. **Lifespan (`@asynccontextmanager`) & Graceful Shutdown**
   - deprecated된 `@app.on_event("startup")` 대신 `lifespan` 컨텍스트 매니저를 사용해 Redis 연결 풀 및 K8s Config(`load_incluster_config()` / `load_kube_config()`)를 초기화하고, 파드 종료(`SIGTERM`) 시 안전하게 정리합니다.
5. **K8s Probe 연동 (`/healthz`, `/readyz`)**
   - 단순 `200 OK`가 아니라, Liveness Probe(`/healthz`)와 Readiness Probe(`/readyz` — Redis ping 및 공유 스토리지 쓰기 가능 여부 확인)의 역할을 구분해 구현합니다.
6. **공식 `kubernetes` Python Client (`BatchV1Api`) 동적 제어**
   - 클러스터 내부에서는 `config.load_incluster_config()`(ServiceAccount 토큰 활용), 로컬 개발 시에는 `config.load_kube_config()`로 자동 폴백(Fallback)하는 패턴을 구현합니다.
   - 대용량 문서 업로드 시 `V1Job`, `V1PodTemplateSpec`, `V1Container`, `V1ResourceRequirements` 객체를 코드로 조립하여 K8s `Job`을 동적 생성하고 상태를 조회합니다.
7. **테스트 주도 학습 (`pytest` + `httpx.AsyncClient`)**
   - 모든 엔드포인트는 `app.dependency_overrides`를 활용한 단위 테스트를 동반하여, 실제 K8s 클러스터나 Redis가 떠 있지 않은 로컬 PC에서도 즉시 검증 가능해야 합니다.

---

## 2. 멀티 아키텍처 & 컨테이너화 주의사항

* 라즈베리파이(`linux/arm64`)와 서브 노트북(`linux/amd64`) 양쪽에서 파드가 스케줄링될 수 있으므로:
  - 모든 파드 응답/작업 결과 메타데이터에 `os.getenv("HOSTNAME")` (파드 이름), `os.getenv("NODE_NAME")` (K8s Downward API로 주입된 노드 이름), `platform.machine()` (아키텍처)을 포함시켜 대시보드에서 한눈에 어느 노드가 처리했는지 확인할 수 있게 합니다.
  - `Dockerfile` 작성 시 멀티 스테이지 빌드 및 non-root 유저(`securityContext.runAsNonRoot`) 실행을 기본으로 연습합니다.
