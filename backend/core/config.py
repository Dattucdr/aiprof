from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AIProf Healthcare Platform"
    environment: str = "development"

    database_url: str = "sqlite:///./aiprof_healthcare.db"

    jwt_secret_key: str = "super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    redis_url: str = "redis://localhost:6379/0"
    GOOGLE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()