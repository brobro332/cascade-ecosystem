---
name: cka-drill-coach
description: >-
  Use this skill when working on Kubernetes manifests, cluster setup, CKA exam preparation,
  troubleshooting scenarios, or when the user asks for CKA practice problems, hints, or grading.
---

# CKA Drill Coach (CKA 실전 코칭 & 채점 스킬)

이 스킬은 사용자가 `Kube-Pipeline` 프로젝트를 구축하면서 **CKA(Certified Kubernetes Administrator)** 시험을 실전처럼 대비할 수 있도록 문제 출제, 힌트 제공, 채점 및 트러블슈팅 훈련을 수행합니다.

## 1. 문제 출제 포맷 (CKA Exam Simulation)

사용자가 특정 단계(예: `02-storage-config`, `04-jobs-rbac-scheduling`)를 진행하거나 `"문제 내줘"`라고 요청하면 실제 CKA 시험 화면처럼 다음 양식으로 미션을 제시합니다:

```markdown
### 📝 [CKA 실전 미션 #번호] 도메인명 (배점 비중: XX%)
* **🎯 기초 개념 & 왜 배우나요?**: (초보자 눈높이에서 이 개념이 무엇인지, 왜 필요한지 쉽게 설명)
* **🔍 무엇을 검색/공부해야 하나요? (초보자 필독 가이드)**:
  - **공식 문서(`kubernetes.io/docs`) 검색어**: `"검색 키워드"` → 문서 내 `어느 섹션` 확인
  - **터미널 도움말로 컨닝하기**: `kubectl create ... --help` 또는 `kubectl explain ...`
  - **핵심 개념 키워드**: (구글이나 공식 문서에서 읽어볼 개념 1~2가지)
* **👣 단계별 진행 가이드 (차근차근 따라 하기)**:
  1. (어느 폴더/터미널에서 무엇을 먼저 확인하는지)
  2. (명령형 CLI로 뼈대를 어떻게 뽑는지 또는 어떤 설정을 넣어야 하는지)
  3. (자신이 한 작업을 스스로 확인해보는 명령어)
```

## 2. 단계별 힌트 & 채점 프로토콜 (Guide → Do → Check)

1. **Step 1 — 가이드 제시 후 대기 (Guide & Stop)**:
   - 절대 정답 YAML을 에이전트가 직접 작성하거나 `kubectl apply`를 대신 실행하지 않습니다.
   - 미션 명세(파일 경로, 요구사항, 명령형 CLI 힌트)만 제시하고 **사용자가 직접 수행할 때까지 턴을 종료하고 기다립니다.**
2. **Step 2 — 채점 실행 (Check & Verify)**:
   - 사용자가 직접 매니페스트를 작성/적용한 뒤 `"다 했어"`, `"체크해 줘"`라고 하면:
     - 매니페스트 정적 검증(`read_file`): 파일 내 필수 필드(Namespace, Label Selector, Volume 이름 일치 여부, Probe 포트, RBAC verbs 등) 확인
     - 클러스터 연결 시 동적 검증: `scripts/cka-grade.sh <step>` 또는 `kubectl get/describe/auth can-i` 명령어를 실행하여 실제 리소스 상태가 `Running` / `Bound`인지 채점합니다.
3. **Step 3 — 오답 피드백 (No Auto-Fix)**:
   - 틀린 부분이 있어도 에이전트가 파일을 직접 수정(`edit_file`)하지 않습니다.
   - 어디가 왜 틀렸는지, 또는 **"어느 명령어(`kubectl describe`, `kubectl logs`, `kubectl get events`)를 치면 원인을 찾을 수 있는지"** 안내하여 사용자가 직접 고치게 합니다.

## 3. 트러블슈팅 (Break & Fix) 시나리오 운영 (`k8s/06-troubleshooting-scenarios/`)

배점 30%를 차지하는 트러블슈팅 훈련 시:
1. 고장 시나리오 스크립트로 일부러 결함(예: Service `selector` 오타, `kube-apiserver` 매니페스트 플래그 오타, NetworkPolicy로 인한 Redis 연결 타임아웃, PVC `storageClassName` 불일치 등)을 발생시킵니다.
2. 사용자에게 **"현재 증상"**만 알려주고 원인을 진단하게 합니다.
3. 사용자가 `kubectl describe`, `crictl`, `journalctl -u kubelet` 등으로 원인을 찾아 복구하면 채점합니다.
