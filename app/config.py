from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    default_admin_username: str = Field(..., env="DEFAULT_ADMIN_USERNAME")
    default_admin_email: str = Field(..., env="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(..., env="DEFAULT_ADMIN_PASSWORD")

    running_in_docker: bool = Field(False, env="RUNNING_IN_DOCKER")

    class Config:
        env_file = ".env"


settings = Settings()