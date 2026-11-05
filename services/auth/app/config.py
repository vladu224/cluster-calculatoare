from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_issuer: str = "grpc://auth:50051"
    token_minutes: int = 60
    grpc_port: int = 50051


settings = Settings()