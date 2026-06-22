from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_user: str = "user"
    db_password: str = "password"
    db_name: str = "store_db"
    test_db_name: str = "store_test_db"

    testing: bool = False

    secret_key: str = "super_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7

    @property
    def database_url(self) -> str:
        db_name = self.test_db_name if self.testing else self.db_name

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
