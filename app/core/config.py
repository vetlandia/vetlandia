from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    APP_NAME: str = "VetLândia"
    APP_VERSION: str = "1.0.0"

    @property
    def db_url(self) -> str:
        """Convert DATABASE_URL to psycopg3 format if needed."""
        url = self.DATABASE_URL
        # Convert postgresql:// to postgresql+psycopg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
