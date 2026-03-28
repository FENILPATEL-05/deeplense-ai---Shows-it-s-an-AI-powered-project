import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL", "postgresql://user:password@localhost:5432/deeplense"
    )
    IMAGES_PROCESSED_DIR: str = os.getenv(
        "IMAGES_PROCESSED_DIR",
        str(Path(__file__).resolve().parent.parent / "images" / "processed"),
    )
    IMAGES_INBOX_DIR: str = os.getenv(
        "IMAGES_INBOX_DIR",
        str(Path(__file__).resolve().parent.parent / "images" / "inbox"),
    )
    IMAGES_FAILED_DIR: str = os.getenv(
        "IMAGES_FAILED_DIR",
        str(Path(__file__).resolve().parent.parent / "images" / "failed"),
    )


settings = Settings()
