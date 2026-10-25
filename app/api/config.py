from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "kube-pipeline-api"
    upload_dir: Path = Path("storage/uploads")
    node_name: str = "local-dev-node"

def get_settings() -> Settings:
    return Settings()