from pydantic import BaseSettings


class Settings(BaseSettings):
    MSSQL_PORT: int | None = None
    MSSQL_PASSWORD: str | None = None
    MSSQL_USER: str
    MSSQL_DB: str
    MSSQL_HOSTNAME: str
    MSSQL_SCHEMA: str
    MSSQl_DRIVER: str

    class Config:
        env_file = './.env'


settings = Settings()
