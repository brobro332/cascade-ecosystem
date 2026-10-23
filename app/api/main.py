from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"service": "kube-pipeline-api", "message": "Hello CKA & FastAPI!"}

@app.get("/healthz")
def read_healthz():
    return {"status": "ok"}