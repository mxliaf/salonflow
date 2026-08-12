from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SalonFlow API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./salonflow.db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Salon operating hours
    SALON_OPEN_TIME: str = "08:00"
    SALON_CLOSE_TIME: str = "18:00"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:4321"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 16:
            raise ValueError(
                "SECRET_KEY deve ser definida via .env ou variável de ambiente. "
                "Gere uma com: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

settings = Settings()
