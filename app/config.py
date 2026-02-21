from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    SECRET_KEY: str = "dev-secret-change-in-production"
    DATABASE_URL: str = "sqlite:///./app.db"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "static/uploads"

    def get_upload_dir(self) -> Path:
        base = Path(__file__).resolve().parent
        p = self.UPLOAD_DIR
        return Path(p) if Path(p).is_absolute() else base / p


settings = Settings()
settings.get_upload_dir().mkdir(parents=True, exist_ok=True)
