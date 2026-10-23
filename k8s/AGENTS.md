# CKA (Certified Kubernetes Administrator) 전용 학습 규칙 (`k8s/AGENTS.md`)

이 디렉토리(`k8s/`) 및 하위 폴더의 매니페스트와 스크립트를 다룰 때는 **CKA 실기 시험장(2시간, 오픈북 `kubernetes.io/docs`만 허용)** 환경을 가정하여 코칭합니다.

> **핵심 진행 원칙 (Guide → User Action → Check)**:
> 에이전트가 매니페스트 파일을 대신 완성하거나 `kubectl apply`를 대신 실행하지 않습니다.
> **초보자도 스스로 찾아서 해결할 수 있도록 [① 눈높이 개념 설명 + ② `kubernetes.io/docs` 검색 키워드 및 `--help`/`explain` 보는 법 + ③ 단계별 따라 하기 가이드]를 먼저 제시 → 사용자가 직접 작성/실행 → 에이전트가 체크(채점)**하는 순서로만 진행합니다.

---

## 1. CKA 실전 CLI 습관 강제 (Imperative First)

1. **처음부터 YAML을 손으로 다 치지 않게 지도할 것**:
   - 항상 아래 환경변수/별칭을 전제로 명령형 생성 명령어를 먼저 안내합니다:
     ```bash
     alias k=kubectl
     export do="--dry-run=client -o yaml"
     export now="--force --grace-period=0"
     ```
   - 예: Deployment 작성 시 바로 YAML을 주기보다 `k create deploy pipeline-api --image=... $do > deploy.yaml` 로 뼈대를 뽑는 방법을 먼저 제시합니다.
2. **`kubectl explain` 활용법 제시**:
   - 기억하기 어려운 중첩 필드(예: `spec.template.spec.affinity.nodeAffinity`, `startupProbe`, `securityContext`, `networkPolicy.spec.ingress`)는 공식 문서 검색어 또는 `kubectl explain pod.spec.containers.livenessProbe --recursive` 명령어를 함께 알려줍니다.
3. **Namespace & Context 확인 습관화**:
   - 모든 문제/작업 시작 시 `-n <namespace>` 또는 `kubectl config set-context --current --namespace=<ns>` 확인을 강조합니다.

---

## 2. CKA 5대 출제 도메인 매핑 & 필수 점검 포인트

각 하위 폴더 작업 시 해당 도메인의 핵심 감점 요인을 반드시 체크합니다:

* **`01-cluster-setup/` (Cluster Architecture, Installation & Configuration - 25%)**
  - `swapoff -a`, 커널 모듈(`overlay`, `br_netfilter`), `sysctl`(`net.ipv4.ip_forward=1`), `containerd`의 `SystemdCgroup = true` 설정
  - `kubeadm init` / `kubeadm join` 토큰 재발급(`kubeadm token create --print-join-command`)
  - **`etcd` 스냅샷 백업 및 복구 (`ETCDCTL_API=3 etcdctl snapshot save/restore`)**: `--cacert`, `--cert`, `--key`, `--endpoints` 4대 인자 암기/추출법 및 복구 시 `/etc/kubernetes/manifests/etcd.yaml`의 `hostPath` 변경 확인
  - 클러스터 버전 업그레이드 순서 (`kubeadm upgrade plan/apply` -> `drain` -> `kubelet/kubectl` 업그레이드 -> `uncordon`)

* **`02-storage-config/` (Storage - 10% & Config)**
  - `PersistentVolume` / `PersistentVolumeClaim` 바인딩 조건 (`storageClassName`, `accessModes`, `capacity`)
  - `hostPath` vs NFS / Local Volume, 파드 내 `volumeMounts` 경로 및 `subPath` 활용
  - `ConfigMap` / `Secret`을 환경변수(`envFrom`, `valueFrom`) 및 볼륨으로 마운트하기

* **`03-workloads-sidecar/` (Workloads & Scheduling - 15%)**
  - **Multi-Container Pod (Sidecar / InitContainer)**: `media-worker`와 `log-sidecar`가 `emptyDir` 볼륨을 공유하여 로그 파일을 읽고 쓰는 구조
  - `livenessProbe`, `readinessProbe`, `startupProbe` 설정
  - 라즈베리파이(ARM64)와 노트북(x86_64) 하이브리드 노드를 고려한 `resources.requests` / `limits` 필수 지정
  - `kubectl rollout status / history / undo`를 통한 무중단 배포 및 롤백

* **`04-jobs-rbac-scheduling/` (RBAC & Scheduling - 25% 연계)**
  - **RBAC**: `pipeline-api` 파드가 K8s API를 호출해 `Job`을 생성할 수 있도록 `ServiceAccount` -> `Role` (`jobs`, `pods`에 대한 `create`, `get`, `list`, `watch`) -> `RoleBinding` 연결 및 `kubectl auth can-i` 검증
  - **Scheduling**: 라즈베리파이 Control-plane Taint(`NoSchedule`) 이해, 무거운 문서 처리 `Job`을 노트북(`k8s-worker-1`, `kubernetes.io/arch=amd64`)에 우선 배치하는 `nodeSelector` / `nodeAffinity` (`preferredDuringSchedulingIgnoredDuringExecution` vs `required...`)
  - `Job`(`completions`, `parallelism`, `backoffLimit`, `ttlSecondsAfterFinished`) 및 `CronJob`(`schedule`)

* **`05-networking-security/` (Services & Networking - 20%)**
  - `ClusterIP`, `NodePort`, `Ingress` (`ingressClassName`, pathType `Prefix`, 라우팅 규칙)
  - CoreDNS(`nslookup kubernetes.default` 테스트 파드 실행)
  - **`NetworkPolicy`**: `redis-queue` 파드에는 오직 `pipeline-api`와 `media-worker` 파드만 6379 포트로 접근 가능하도록 Ingress/Egress 격리 (라벨 셀렉터 주의)

* **`06-troubleshooting-scenarios/` (Troubleshooting - 30%, 최고 배점)**
  - Control Plane 장애(`/etc/kubernetes/manifests/*.yaml` 오타/경로 오류 → `crictl ps -a`, `crictl logs`, `/var/log/pods` 확인)
  - Worker Node `NotReady` (`systemctl status kubelet`, `journalctl -u kubelet -xe`, 인증서/설정 경로 오류 복구)
  - Service/Network 연결 불가 (Service `selector` 라벨 불일치, `targetPort` vs `containerPort` 불일치, `kubectl get ep` 확인)
