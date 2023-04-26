from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://USER:PASSWORD@HOST:PORT/NAME_DB'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    email_username: str = 'mail@ex.ua'
    email_password: str = 'password'
    email_from: str = 'mail@ex.ua'
    email_port: int = 465
    email_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'name'
    cloudinary_api_key: int = '12345678987654321'
    cloudinary_api_secret: str = 'secret_key'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
