from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    project_name: str = Field("BookReady API", description="Service title")
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    database_url: str = Field("sqlite+aiosqlite:///./bookready.db", env="DATABASE_URL")
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")

    s3_endpoint: str = Field(..., env="S3_ENDPOINT")
    s3_region: str = Field("us-east-1", env="S3_REGION")
    s3_access_key: str = Field(..., env="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., env="S3_SECRET_KEY")
    s3_bucket: str = Field("bookready", env="S3_BUCKET")
    s3_presign_expiry: int = Field(600, env="S3_PRESIGN_EXPIRY")

    clamav_host: str = Field("clamav", env="CLAMAV_HOST")
    clamav_port: int = Field(3310, env="CLAMAV_PORT")

    media_root: Path = Field(Path("/tmp/bookready"), env="MEDIA_ROOT")
    report_media_root: Path = Field(Path("/tmp/bookready/reports"), env="REPORT_MEDIA_ROOT")

    paper_data_path: Path = Field(Path(__file__).resolve().parent.parent / "data" / "paper_thickness.json")

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"

    @validator("media_root", "report_media_root", pre=True)
    def _ensure_path(cls, value: str | Path) -> Path:  # type: ignore[override]
        if isinstance(value, Path):
            return value
        return Path(value)

    @validator("paper_data_path", pre=True)
    def _default_paper_data(cls, value: Optional[str | Path]) -> Path:  # type: ignore[override]
        if value:
            return Path(value)
        return Path(__file__).resolve().parent.parent / "data" / "paper_thickness.json"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.media_root.mkdir(parents=True, exist_ok=True)
    settings.report_media_root.mkdir(parents=True, exist_ok=True)
    return settings
