# 🎓 CKA & FastAPI 마스터 학습 로드맵 (`LEARNING_ROADMAP.md`)

> 이 문서는 `Kube-Pipeline` 프로젝트를 진행하며 **CKA 시험 5대 도메인(100%)**과 **FastAPI 실전 역량**을 하나씩 정복하기 위한 진도표(Harness Tracker)입니다. 각 단계 완료 시 체크박스(`[x]`)를 업데이트합니다.

---

## Track A: CKA (Certified Kubernetes Administrator) 정복 트랙

### Phase 1. Cluster Architecture, Installation & Configuration (배점 25%) — `k8s/01-cluster-setup/`
- [ ] **1-1. 사전 환경 구성**: `swapoff`, 커널 모듈(`overlay`, `br_netfilter`), `sysctl` 네트워크 포워딩, `containerd` 설치 및 `SystemdCgroup = true` 설정
- [ ] **1-2. Control Plane 초기화 (`kubeadm init`)**: 라즈베리파이 8GB 마스터 노드 초기화, `kubeconfig` 설정, CNI(Flannel/Calico) 배포
- [ ] **1-3. Taint 제어**: 마스터 노드 단독 구동이 가능하도록 Control-plane `NoSchedule` Taint 해제 및 복원 실습 (`kubectl taint nodes ...`)
- [ ] **1-4. 워커 노드 합류 & 라이프사이클**: 서브 노트북(`k8s-worker-1`) `kubeadm join`, 실습 종료 시 `cordon` / `drain` / `uncordon` 숙달
- [ ] **1-5. `etcd` 백업 및 복구 (CKA 단골 문제)**: `etcdctl snapshot save` 및 `etcdctl snapshot restore` 실전 연습

### Phase 2. Storage & Configuration (배점 10%) — `k8s/02-storage-config/`
- [ ] **2-1. Namespace & ConfigMap/Secret**: `kube-pipeline` 네임스페이스 생성, 환경설정(`ConfigMap`) 및 민감정보(`Secret`) 명령형 생성(`$do`)
- [ ] **2-2. PersistentVolume (PV) & PersistentVolumeClaim (PVC)**: 미디어/문서 원본 및 결과물을 저장할 공유 스토리지(`HostPath` / `NFS`) 바인딩
- [ ] **2-3. Pod 볼륨 마운트 & 환경변수 주입**: `envFrom`, `valueFrom`, `volumeMounts` 실습

### Phase 3. Workloads & Multi-Container Pod (배점 15%) — `k8s/03-workloads-sidecar/`
- [ ] **3-1. Redis Queue 배포**: `redis:alpine` Deployment, `resources.requests/limits` 설정
- [ ] **3-2. Multi-Container Sidecar 패턴 (CKA 필수)**: `media-worker` 컨테이너와 `log-sidecar`(`busybox`) 컨테이너가 `emptyDir` 볼륨을 공유해 실시간 로그를 스트리밍하는 Pod/Deployment 구성
- [ ] **3-3. Liveness / Readiness / Startup Probe**: `pipeline-api`의 `/healthz`, `/readyz` 엔드포인트와 K8s Probe 연동
- [ ] **3-4. Rolling Update & Rollback**: 이미지 태그 업데이트 및 `kubectl rollout undo` 실습

### Phase 4. RBAC, Jobs & Advanced Scheduling (배점 25% 연계) — `k8s/04-jobs-rbac-scheduling/`
- [ ] **4-1. ServiceAccount & RBAC (`Role`, `RoleBinding`)**: `pipeline-api` 파드가 K8s API로 `Job`을 생성/조회할 수 있는 최소 권한 부여 및 `kubectl auth can-i` 검증
- [ ] **4-2. K8s `Job` & `CronJob`**: 대용량 문서 분석 일회성 `Job`(`completions`, `backoffLimit`, `ttlSecondsAfterFinished`) 및 만료 파일 정리 `CronJob` 작성
- [ ] **4-3. NodeSelector & NodeAffinity**: 무거운 작업을 고성능 노트북(`k8s-worker-1`, `amd64`)에 우선 배치하되, 노트북이 꺼져 있을 때는 라즈베리파이(`arm64`)에서도 돌아가도록 `preferredDuringSchedulingIgnoredDuringExecution` 설정

### Phase 5. Services, Networking & NetworkPolicy (배점 20%) — `k8s/05-networking-security/`
- [ ] **5-1. Service (`ClusterIP`, `NodePort`) & CoreDNS 검증**: 내부 서비스 디스커버리(`redis-queue.kube-pipeline.svc.cluster.local`) 확인
- [ ] **5-2. Ingress Controller & Ingress 라우팅**: `/` 및 `/api` 경로 기반 트래픽 라우팅 구성
- [ ] **5-3. `NetworkPolicy` (CKA 고난도 단골)**: `redis-queue` 파드에는 오직 `app=pipeline-api` 및 `app=media-worker` 라벨을 가진 파드만 6379 포트로 접근 허용

### Phase 6. Troubleshooting Scenarios (배점 30%, 최고 배점) — `k8s/06-troubleshooting-scenarios/`
- [ ] **6-1. 시나리오 1 (App Failure)**: ImagePullBackOff, CrashLoopBackOff, ConfigMap 키 오타, VolumeMount 경로 불일치 복구
- [ ] **6-2. 시나리오 2 (Networking Failure)**: Service Selector 라벨 불일치, TargetPort 오타, NetworkPolicy 차단 디버깅(`kubectl get ep`)
- [ ] **6-3. 시나리오 3 (Control Plane & Node Failure)**: `/etc/kubernetes/manifests/kube-apiserver.yaml` 오타 복구, `kubelet` 서비스 장애(`journalctl -u kubelet`) 복구

---

## Track B: FastAPI & Python K8s SDK 정복 트랙 — `app/`

- [ ] **F-1. 프로젝트 구조 & Lifespan 설계 (`app/api/main.py`)**: `@asynccontextmanager` 기반 Lifespan, `/healthz` & `/readyz` Probe 엔드포인트 구현
- [ ] **F-2. Pydantic v2 스키마 & `pydantic-settings` (`app/api/schemas.py`, `config.py`)**: 환경변수 바인딩, 작업 상태 Enum, 요청/응답 모델 검증
- [ ] **F-3. 의존성 주입 (`Depends`) & 비동기 파일 업로드 (`UploadFile`)**: 대용량 파일을 메모리에 다 올리지 않고 청크 단위로 안전하게 공유 스토리지(PVC)에 저장하고 Redis 큐에 적재
- [ ] **F-4. `async def` vs `def` & 백그라운드 워커 (`app/worker/`)**: Pillow 이미지 리사이징/워터마크 및 문서 요약 워커 구현 (노드/파드/아키텍처 메타데이터 기록)
- [ ] **F-5. 공식 `kubernetes` Python Client 연동 (`app/api/k8s_client.py`)**: `BatchV1Api`를 사용하여 FastAPI 엔드포인트에서 K8s `Job`을 동적으로 생성하고 파드 상태를 조회
- [ ] **F-6. 테스트 하네스 (`tests/`)**: `pytest` + `httpx.AsyncClient` + `dependency_overrides`로 K8s/Redis 모킹 단위 테스트 작성
- [ ] **F-7. 멀티 아키텍처 빌드 (`docker buildx`)**: `linux/arm64`(라즈베리파이) + `linux/amd64`(노트북) 동시 지원 이미지 빌드 및 배포
