import pytest
from fastapi.testclient import TestClient
from app.api.main import app, jobs_db
from app.api.config import Settings, get_settings
from pathlib import Path

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_jobs_db():
    jobs_db.clear()

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_get_job():
    response1 = client.post("/jobs", json={"task_type": "resize", "target_file": "photo.png", "priority": 2})
    assert response1.status_code == 201

    job_data = response1.json()
    job_id = job_data["job_id"]

    response2 = client.get(f"/jobs/{job_id}")
    assert response2.status_code == 200
    assert response2.json()["target_file"] == "photo.png"

def test_get_nonexistent_job_returns_404():
    response = client.get("/jobs/job-ghost-999")
    assert response.status_code == 404

def test_list_jobs_filter_and_limit():
    json1 = {"task_type": "resize", "target_file": "photo1.png", "priority": 3}
    json2 = {"task_type": "resize", "target_file": "photo2.png", "priority": 4}
    
    client.post("/jobs", json=json1)
    client.post("/jobs", json=json2)

    response1 = client.get("/jobs?status=pending")
    response2 = client.get("/jobs?status=completed")
    response3 = client.get("/jobs?limit=1")

    assert len(response1.json()) == 0
    assert len(response2.json()) == 2
    assert len(response3.json()) == 1

def test_invalid_job_returns_422():
    response1 = client.post("/jobs", json={"task_type": "resize", "target_file": "photo.png", "priority": 99})
    response2 = client.get("/jobs?limit=100")

    assert response1.status_code == 422
    assert response2.status_code == 422

def test_upload_job_success():
    response = client.post(
        "/jobs/upload",
        files={"file": ("test_image.png", b"fake-image-binary-content", "image/png")},
        data={"task_type": "watermark", "priority": "1"},
    )

    assert response.status_code == 201
    assert response.json()["target_file"] == "test_image.png"
    assert response.json()["task_type"] == "watermark"
    assert Path("storage/uploads/test_image.png").exists()

def test_upload_empty_file_returns_400():
    response = client.post(
        "/jobs/upload",
        files={"file": ("test_image.png", b"", "image/png")},
        data={"task_type": "watermark", "priority": "1"},
    )

    assert response.status_code == 400

def test_settings_override(tmp_path: Path):
    def get_test_settings() -> Settings:
        return Settings(upload_dir=tmp_path, node_name="k8s-worker-laptop")

    app.dependency_overrides[get_settings] = get_test_settings

    try:
        root_res = client.get("/")
        assert root_res.status_code == 200
        assert root_res.json()["node_name"] == "k8s-worker-laptop"

        up_res = client.post(
            "/jobs/upload",
            files={"file": ("override_test.txt", b"hello-k8s", "text/plain")},
        )
        assert up_res.status_code == 201
        assert (tmp_path / "override_test.txt").exists()
    finally:
        app.dependency_overrides.clear()

def test_readyz_and_background_worker():
    response1 = client.get("/readyz")
    assert response1.status_code == 200
    assert response1.json()["status"] == "ready"

    response2 = client.post("/jobs", json={"task_type": "resize", "target_file": "photo1.png", "priority": 3})
    assert response2.json()["status"] == "pending"

    response3 = client.get(f"/jobs/{response2.json()["job_id"]}")
    assert response3.json()["status"] == "completed"