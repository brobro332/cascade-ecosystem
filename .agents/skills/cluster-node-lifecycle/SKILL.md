---
name: cluster-node-lifecycle
description: >-
  Use this skill when turning the secondary laptop worker node (k8s-worker-1) on or off,
  checking hybrid cluster node status (Raspberry Pi master + laptop worker),
  performing cordon/drain/uncordon operations, or backing up etcd.
---

# Cluster Node Lifecycle (하이브리드 홈랩 전원 & 노드 관리 스킬)

라즈베리파이 8GB(`k8s-control-plane`, 24시간 구동)와 서브 노트북 16GB(`k8s-worker-1`, 온디맨드 구동)로 구성된 하이브리드 클러스터의 시작/종료 절차를 CKA 실전 문제와 연계하여 수행합니다.

## 1. 공부 시작 루틴 (서브 노트북 전원 On 시)

1. 노드 상태 및 Taint 확인:
   ```bash
   kubectl get nodes -o wide
   kubectl describe node k8s-worker-1 | grep -E "Taints|Unschedulable"
   ```
2. 이전 종료 시 `drain`/`cordon` 되어 `SchedulingDisabled` 상태라면 스케줄링 재개:
   ```bash
   kubectl uncordon k8s-worker-1
   ```
3. 필요 시 워커 파드 스케일 업 또는 재배치 확인:
   ```bash
   kubectl get pods -n kube-pipeline -o wide
   ```

## 2. 공부 종료 루틴 (서브 노트북 전원 Off 전 필수 CKA 실습)

노트북을 그냥 끄면 5분간(`node-monitor-grace-period` + `pod-eviction-timeout`) 파드가 `Terminating`/`Unknown` 상태로 방치됩니다. 항상 CKA 시험 문제와 동일하게 안전 대피를 수행합니다:

1. 노트북 노드의 스케줄링 차단 및 파드 퇴거(Eviction):
   ```bash
   kubectl drain k8s-worker-1 --ignore-daemonsets --delete-emptydir-data
   ```
2. 모든 워크로드 파드가 라즈베리파이(`k8s-control-plane`)로 정상 이동해 `Running` 상태인지 확인:
   ```bash
   kubectl get pods -n kube-pipeline -o wide
   ```
3. 주요 실습을 마친 날에는 `etcd` 스냅샷 백업 수행 여부 확인.
