from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:pasword@host:port/name_db'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    email_username: str = 'mail@ex.ua'
    email_password: str = 'password'
    email_from: str = 'mail@ex.ua'
    email_port: str = '465'
    email_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: str = '6379'
    cloudinary_name: str = 'name'
    cloudinary_api_key: str = '12345678987654321'
    cloudinary_api_secret: str = 'secret_key'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
