from pathlib import Path
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    SECRET_KEY: str = "dev-secret-change-in-production"
    DATABASE_URL: str | None = None
    RDS_HOSTNAME: str | None = None
    RDS_PORT: str | None = None
    RDS_DB_NAME: str | None = None
    RDS_USERNAME: str | None = None
    RDS_PASSWORD: str | None = None

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "static/uploads"
    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        if self.DATABASE_URL:
            return self
        if all(
            (
                self.RDS_HOSTNAME,
                self.RDS_PORT,
                self.RDS_DB_NAME,
                self.RDS_USERNAME is not None,
                self.RDS_PASSWORD is not None,
            )
        ):
            user = quote_plus(self.RDS_USERNAME)
            password = quote_plus(self.RDS_PASSWORD)
            self.DATABASE_URL = (
                f"postgresql://{user}:{password}@"
                f"{self.RDS_HOSTNAME}:{self.RDS_PORT}/{self.RDS_DB_NAME}"
            )
            return self
        raise ValueError(
            "Set DATABASE_URL or all of RDS_HOSTNAME, RDS_PORT, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD"
        )

    def get_upload_dir(self) -> Path:
        base = Path(__file__).resolve().parent
        p = self.UPLOAD_DIR
        return Path(p) if Path(p).is_absolute() else base / p


settings = Settings()
assert settings.DATABASE_URL is not None  # set by validator from DATABASE_URL or RDS_*

settings.get_upload_dir().mkdir(parents=True, exist_ok=True)
