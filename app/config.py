from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "מערכת ניהול בית הקפה"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production-use-long-random-string"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cafe_mgmt"

    # WhatsApp Cloud API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "cafe-verify-token-change-me"
    WHATSAPP_API_VERSION: str = "v20.0"

    # Cafe network restriction (comma-separated public IPs or CIDR)
    CAFE_ALLOWED_IPS: str = ""  # e.g. "1.2.3.4,5.6.7.0/24"
    REQUIRE_CAFE_NETWORK: bool = True

    # Session
    SESSION_EXPIRE_DAYS: int = 90
    COOKIE_NAME: str = "cafe_session"

    # Storage (Cloudflare R2 / S3 compatible)
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: str = "cafe-photos"
    S3_REGION: str = "auto"
    PHOTO_RETENTION_DAYS: int = 60

    # Timezone
    TIMEZONE: str = "Asia/Jerusalem"

    # Breaks defaults (will be overridden by settings table / labor consult)
    DEFAULT_BREAK_MINUTES: int = 30
    BREAK_REMINDER_MINUTES_BEFORE: int = 5

    # Constraints deadline
    CONSTRAINTS_DEADLINE_WEEKDAY: int = 2  # Wednesday = 2 (0=Mon)
    CONSTRAINTS_DEADLINE_HOUR: int = 13
    CONSTRAINTS_DEADLINE_MINUTE: int = 0

    # Background worker
    QUEUE_POLL_SECONDS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
