from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_uri: str
    db_name: str = "paperpilot"
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()