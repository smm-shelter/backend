from functools import cached_property

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ADMIN_PATH: str

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    S3_USER_HOST: HttpUrl
    S3_API_HOST: HttpUrl
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str

    @cached_property
    def s3_url(self):
        return str(self.S3_API_HOST)

    @cached_property
    def s3_resource_url(self):
        return f"{self.S3_USER_HOST}{self.S3_BUCKET_NAME}"

    @cached_property
    def postgres_url(self):
        return (
            "postgresql+asyncpg://"
            + f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            + f"{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        )


settings = Settings()  # type: ignore
