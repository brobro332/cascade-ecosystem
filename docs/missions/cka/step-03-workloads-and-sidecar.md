# 🎯 [CKA Mission 03] 죽어도 살아나는 `Deployment` & CKA 단골 `Multi-Container Sidecar` 파드

> **난이도**: ★★★☆☆ (CKA 핵심 빈출!)  
> **CKA 출제 비중**: Workloads & Scheduling (15% — 특히 Sidecar 컨테이너 + `emptyDir` 볼륨 공유는 CKA 시험 단골 1순위 문제!)  
> **연계 FastAPI 코드**: Step 1의 `/healthz`(Liveness Probe) 및 Step 7의 `/readyz`(Readiness Probe) 쿠버네티스 실전 연결!  
> **작업 대상 폴더**: `k8s/03-workloads-sidecar/`  

---

## 1️⃣ 눈높이 개념 설명 (Why & Concept)

### 💡 1. 왜 그냥 `Pod`로 안 띄우고 `Deployment`로 띄울까요? ("파드 자동 부활 장치 & 분신술!")
* 미션 1, 2에서 우리가 만든 단독 `Pod`(`pipeline-storage-pod`)는 치명적인 약점이 있습니다: **누가 실수로 파드를 지우거나 컴퓨터 에러로 파드가 죽으면, 그냥 영원히 죽고 끝납니다!**
* 그래서 실무에서는 단독 `Pod`를 거의 직접 만들지 않고, **`Deployment`(파드 관리 감독관)**를 만듭니다!
* **`Deployment` 감독관이 해주는 3가지 마법**:
  1. **분신술 (`replicas: 2`)**: "우리 FastAPI 파드를 항상 **2개씩** 띄워놔라!"
  2. **불사조 부활 (Self-Healing)**: 만약 2개 중 1개 파드를 내가 강제로 삭제(`kubectl delete pod`)해 버리면? 감독관이 0.1초 만에 **"어?! 왜 1개밖에 없지? 당장 새 파드 1개 더 만들어!"** 하고 자동으로 다시 2개를 맞춰 놓습니다!
  3. **무중단 업데이트 & 롤백 (`rollout undo`)**: 새 버전(v2)으로 바꿀 때 손님이 끊기지 않게 하나씩 교체하고, 문제 생기면 1초 만에 이전 버전(v1)으로 되돌립니다.

---

### 💡 2. `livenessProbe`(`/healthz`) & `readinessProbe`(`/readyz`) 연결!
우리가 FastAPI 트랙 Step 1과 Step 7에서 만들어 두었던 두 주소를 드디어 쿠버네티스 감독관에게 알려줄 차례입니다!
* **`livenessProbe` (`/healthz`)**: 쿠버네티스가 10초마다 `/healthz`를 찔러서 응답이 없으면 **"이 파드 기절했네! 재시작시켜!"** 하고 살려냅니다.
* **`readinessProbe` (`/readyz`)**: 쿠버네티스가 `/readyz`를 찔러서 `200 OK`가 나올 때만 손님 요청을 보내줍니다.

---

### 💡 3. CKA 시험 100% 출제 유형: **멀티 컨테이너 사이드카(`Sidecar`) 패턴 & `emptyDir`**
* **사이드카(`Sidecar`)란?**: 오토바이 옆에 붙은 보조 좌석처럼, **하나의 파드(원룸 방 1개) 안에 '메인 컨테이너(일꾼)'와 '보조 컨테이너(사이드카)' 2명이 함께 사는 구조**입니다!
* **CKA 시험에 맨날 나오는 문제 시나리오**:
  * *"메인 컨테이너(`worker`)가 `/var/log/pipeline/worker.log` 파일에 계속 작업 기록(로그)을 쓰고 있다."*
  * *"같은 파드 안에 `busybox` 이미지를 쓰는 사이드카 컨테이너(`log-sidecar`)를 추가해서, 두 컨테이너가 **`emptyDir` 공유 폴더**를 같이 쓰면서 사이드카가 그 로그 파일을 실시간으로 화면에 출력(`tail -f`)하게 만드시오!"*
* **`emptyDir` 볼륨이란?**: 미션 2에서 배운 `PV/PVC`가 거창한 외장하드라면, **`emptyDir`은 한 파드 안에 사는 룸메이트 컨테이너 둘이서만 같이 쓰는 '거실 공용 탁자(임시 공유 폴더)'**입니다! (파드가 사라지면 같이 사라지는 가벼운 폴더)

---

## 2️⃣ 뭘 검색/공부해야 해결할 수 있나요? (Search & Study Guide)

* **📘 쿠버네티스 공식 문서 (`https://kubernetes.io/ko/docs/`)**:
  1. **검색어: `"Configure Liveness, Readiness and Startup Probes"`** (한글: **`"활성(Liveness), 준비성(Readiness) 및 스타트업 프로브 구성"`**)
     * 문서 내 **`HTTP 활성 프로브 정의`** 섹션에서 `livenessProbe:` 아래 `httpGet: path: /healthz, port: 8000` YAML 구조를 눈으로 확인하세요!
  2. **검색어: `"Volumes"` 또는 `"emptyDir"`**
     * 파드 맨 아래 `volumes: - name: log-volume, emptyDir: {}` 한 줄로 공유 폴더를 만드는 법 확인!
* **💻 터미널 `-h` 컨닝법**:
  * `kubectl create deployment -h`

---

## 3️⃣ 단계별 따라 하기 가이드 (Step-by-Step Checklist)

### [Step 3-1] 이전 미션 2의 단독 파드 정리하기
깔끔한 실습을 위해 미션 2에서 띄웠던 단독 파드(`pipeline-storage-pod`)만 먼저 내려줍니다 (`PV`, `PVC`, `ConfigMap`, `Secret`은 그대로 둡니다!):

```powershell
kubectl delete pod pipeline-storage-pod -n kube-pipeline --force --grace-period=0
```

---

### [Step 3-2] 우리 FastAPI 앱을 `Deployment`(2개 복제본 + Probe 장착)로 띄우기! (`01-api-deployment.yaml`)

1. 먼저 명령어로 Deployment 뼈대를 뽑아보는 연습을 해봅니다 (확인만 해보기):
   `kubectl create deployment pipeline-api -n kube-pipeline --image=kube-pipeline-api:v1 --replicas=2 --port=8000 --dry-run=client -o yaml`
2. 여기에 `ConfigMap`, `PVC`, 그리고 **`livenessProbe`(`GET /healthz`) / `readinessProbe`(`GET /readyz`)**를 합친 `k8s/03-workloads-sidecar/01-api-deployment.yaml` 파일을 만들고 아래 내용을 작성해 보세요:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pipeline-api
  namespace: kube-pipeline
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pipeline-api
  template:
    metadata:
      labels:
        app: pipeline-api
    spec:
      containers:
        - name: api
          image: kube-pipeline-api:v1
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: pipeline-config
            - secretRef:
                name: pipeline-secret
          # FastAPI에서 만들었던 /healthz 와 /readyz 연결!
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
          volumeMounts:
            - name: shared-storage
              mountPath: "/app/storage/uploads"
      volumes:
        - name: shared-storage
          persistentVolumeClaim:
            claimName: pipeline-pvc
```

3. 배포하고 **파드 2개가 동시에 뜨는지** 확인해 보세요!
   ```powershell
   kubectl apply -f k8s/03-workloads-sidecar/01-api-deployment.yaml
   kubectl get pods -n kube-pipeline
   ```
4. **불사조 부활(Self-Healing) 직접 실험해 보기!**
   위에서 조회된 `pipeline-api-...` 파드 2개 중 아무거나 하나의 이름을 복사해서 강제로 죽여보세요:
   ```powershell
   kubectl delete pod <파드이름1개> -n kube-pipeline --force --grace-period=0
   kubectl get pods -n kube-pipeline
   ```
   지우자마자 감독관(`Deployment`)이 **새로운 파드를 즉시 만들어서 다시 2개를 채워놓는 것(`AGE: 2s`)**이 보이시나요?! 😮

---

### [Step 3-3] CKA 시험 단골 문제! 멀티 컨테이너 사이드카 파드 만들기 (`02-worker-sidecar.yaml`)

이번엔 파드 1개 안에 **2명의 컨테이너(`main-worker` + `log-sidecar`)**가 살면서, **`emptyDir` 볼륨(`/var/log/pipeline`)을 공유**하는 매니페스트를 작성합니다.  
`k8s/03-workloads-sidecar/02-worker-sidecar.yaml` 파일을 새로 만들고 작성해 보세요:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: media-worker
  namespace: kube-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: media-worker
  template:
    metadata:
      labels:
        app: media-worker
    spec:
      containers:
        # [컨테이너 1] 메인 워커: 5초마다 공유 폴더의 worker.log 파일에 작업 로그를 기록함
        - name: main-worker
          image: busybox:1.36
          command: ["/bin/sh", "-c"]
          args:
            - >
              while true; do
                echo "$(date) [Worker] Processing media queue on $(hostname)..." >> /var/log/pipeline/worker.log;
                sleep 5;
              done
          volumeMounts:
            - name: log-share
              mountPath: /var/log/pipeline

        # [컨테이너 2] 로그 사이드카: 같은 공유 폴더(/var/log/pipeline)를 마운트해서 worker.log를 실시간 출력!
        - name: log-sidecar
          image: busybox:1.36
          command: ["/bin/sh", "-c", "tail -n+1 -f /var/log/pipeline/worker.log"]
          volumeMounts:
            - name: log-share
              mountPath: /var/log/pipeline

      # 두 컨테이너가 함께 쓰는 '거실 공용 탁자(emptyDir)' 볼륨!
      volumes:
        - name: log-share
          emptyDir: {}
```

1. 배포하고 파드 상태를 확인해 보세요:
   ```powershell
   kubectl apply -f k8s/03-workloads-sidecar/02-worker-sidecar.yaml
   kubectl get pods -n kube-pipeline
   ```
   * 주목할 점: `media-worker-...` 파드의 **`READY` 칸이 `1/1`이 아니라 `2/2` (방 1개에 컨테이너 2명 모두 실행 중!)**로 뜨는 것을 확인하세요!
2. **사이드카 컨테이너(`log-sidecar`)가 메인 워커의 로그를 잘 읽고 있는지 확인**:
   ```powershell
   kubectl logs -n kube-pipeline deployment/media-worker -c log-sidecar
   ```
   `main-worker`가 파일에 적은 글자를 `log-sidecar`가 읽어서 화면에 쫙 보여주는지 확인해 보세요!

---

## 4️⃣ 완료 및 체크 요청
1. `pipeline-api` 파드 2개(`1/1`)와 `media-worker` 파드 1개(`2/2`)가 모두 `Running`이고,
2. `log-sidecar` 로그가 잘 출력된다면,  
**"CKA 미션 3 다 했어, 체크해줘!"**라고 말씀해 주세요!
