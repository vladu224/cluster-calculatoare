# reads settings from environment variables
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    admin_username: str = "admin"
    admin_email: str = "admin@cluster.local"
    admin_password: str


settings = Settings()