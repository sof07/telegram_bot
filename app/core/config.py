from pydantic_settings import BaseSettings


# Временно для тестов
class Settings(BaseSettings):
    management_bot_token: str = 'MANAGEMENT_BOT_TOKEN'
    report_bot_token: str = 'REPORT_BOT_TOKEN'
    database_url: str = 'DATABASE_URL'
    api_hash: str = 'API_HASH'
    api_id: int = 'API_ID'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()
