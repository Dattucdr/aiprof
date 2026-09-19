from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AIProf Healthcare Platform"
    environment: str = "development"

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
    GOOGLE_API_KEY: str
    

settings = Settings()