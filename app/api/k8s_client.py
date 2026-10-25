from kubernetes import client, config
from app.api.schemas import JobCreateRequest

def build_k8s_job_object(job_id: str, job_req: JobCreateRequest) -> client.V1Job:
    """
    JobCreateRequest를 받아 쿠버네티스 표준 batch/v1 V1Job 매니페스트 객체를 조립합니다.
    """
    container = client.V1Container(
        name="heavy-worker",
        image="kube-pipeline-worker:latest",
        command=["python", "-m", "app.worker.cli", "--file", job_req.target_file, "--task", job_req.task_type.value],
    )

    pod_spec = client.V1PodSpec(
        restart_policy="Never",
        containers=[container],
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "kube-pipeline-job", "job_id": job_id}),
        spec=pod_spec,
    )
    job_spec = client.V1JobSpec(
        template=template,
        backoff_limit=2,
        ttl_seconds_after_finished=300,
    )

    return client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_id),
        spec=job_spec,
    )

class K8sJobDispatcher:
    """K8s 클러스터에 Job을 생성하는 디스패처 (Depends 주입 대상)"""

    def dispatch(self, namespace: str, k8s_job: client.V1Job) -> str:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        batch_v1 = client.BatchV1Api()
        created = batch_v1.create_namespaced_job(namespace=namespace, body=k8s_job)
        return created.metadata.name


def get_k8s_dispatcher() -> K8sJobDispatcher:
    return K8sJobDispatcher()