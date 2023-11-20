from pydantic import BaseSettings


class Settings(BaseSettings):
    MSSQL_PORT: int
    MSSQL_PASSWORD: str
    MSSQL_USER: str
    MSSQL_DB: str
    MSSQL_HOSTNAME: str
    MSSQL_SCHEMA: str
    MSSQl_DRIVER: str

    class Config:
        env_file = './.env'


settings = Settings()
