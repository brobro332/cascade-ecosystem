#!/usr/bin/env bash
# ==============================================================================
# CKA Self-Grading & Verification Harness (cka-grade.sh)
# 사용법: ./scripts/cka-grade.sh [01|02|03|04|05|all]
# ==============================================================================
set -euo pipefail

NS="kube-pipeline"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

check_step_01() {
    info "=== Phase 01: Cluster Setup 검증 (배점 25%) ==="
    if kubectl get nodes &>/dev/null; then
        READY_NODES=$(kubectl get nodes --no-headers | grep -c " Ready" || true)
        if [ "$READY_NODES" -ge 1 ]; then
            pass "클러스터 연결 성공 (Ready 노드 수: ${READY_NODES})"
            kubectl get nodes -o wide
        else
            fail "Ready 상태인 노드가 없습니다. 'kubectl describe nodes'로 CNI 및 kubelet 상태를 확인하세요."
        fi
    else
        fail "kubectl로 클러스터에 접근할 수 없습니다. ~/.kube/config를 확인하세요."
    fi
}

check_step_02() {
    info "=== Phase 02: Storage & Config 검증 (배점 10%) ==="
    if kubectl get ns "$NS" &>/dev/null; then
        pass "Namespace '$NS' 존재 확인"
    else
        fail "Namespace '$NS'가 없습니다. (힌트: kubectl create ns $NS)"
        return
    fi

    PVC_STATUS=$(kubectl get pvc -n "$NS" -o jsonpath='{.items[*].status.phase}' 2>/dev/null || true)
    if [[ "$PVC_STATUS" == *"Bound"* ]]; then
        pass "PVC Bound 상태 확인 ($PVC_STATUS)"
    else
        fail "Bound된 PVC가 없습니다 (현재 상태: ${PVC_STATUS:-없음}). 'kubectl describe pvc -n $NS'로 원인을 확인하세요."
    fi
}

check_step_03() {
    info "=== Phase 03: Workloads & Sidecar 검증 (배점 15%) ==="
    WORKER_CONTAINERS=$(kubectl get pods -n "$NS" -l app=media-worker -o jsonpath='{.items[0].spec.containers[*].name}' 2>/dev/null || true)
    if [[ $(echo "$WORKER_CONTAINERS" | wc -w) -ge 2 ]]; then
        pass "Multi-Container (Sidecar) 파드 구성 확인: 컨테이너 목록 [$WORKER_CONTAINERS]"
    else
        fail "media-worker 파드에 Sidecar 컨테이너가 확인되지 않습니다. (현재: ${WORKER_CONTAINERS:-파드 없음})"
    fi
}

check_step_04() {
    info "=== Phase 04: RBAC, Jobs & Scheduling 검증 (배점 25%) ==="
    CAN_CREATE_JOB=$(kubectl auth can-i create jobs --as="system:serviceaccount:${NS}:pipeline-api-sa" -n "$NS" 2>/dev/null || true)
    if [ "$CAN_CREATE_JOB" == "yes" ]; then
        pass "RBAC 검증 통과: ServiceAccount 'pipeline-api-sa'가 Job 생성 권한을 가지고 있습니다."
    else
        fail "RBAC 검증 실패: 'pipeline-api-sa'가 Job을 생성할 수 없습니다 (결과: $CAN_CREATE_JOB). Role 및 RoleBinding을 확인하세요."
    fi
}

check_step_05() {
    info "=== Phase 05: Networking & NetworkPolicy 검증 (배점 20%) ==="
    NP_COUNT=$(kubectl get netpol -n "$NS" --no-headers 2>/dev/null | wc -l || true)
    if [ "$NP_COUNT" -ge 1 ]; then
        pass "NetworkPolicy 리소스 존재 확인 (${NP_COUNT}개)"
    else
        fail "Namespace '$NS'에 적용된 NetworkPolicy가 없습니다."
    fi
}

STEP="${1:-all}"
case "$STEP" in
    01) check_step_01 ;;
    02) check_step_02 ;;
    03) check_step_03 ;;
    04) check_step_04 ;;
    05) check_step_05 ;;
    all)
        check_step_01
        check_step_02
        check_step_03
        check_step_04
        check_step_05
        ;;
    *)
        echo "사용법: $0 [01|02|03|04|05|all]"
        exit 1
        ;;
esac
