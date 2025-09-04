from pydantic_settings import BaseSettings, SettingsConfigDict

BDD_FILE_PROFILES: dict[str, str] = {
    "dev": "http://10.200.65.13:2015",
    "beta": "http://10.200.65.13:2015",
    "prod": "http://bdd-gateway:80/api/file",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="BDD_FILE_", case_sensitive=False, extra="ignore"
    )

    # 服务端配置
    PROFILE: str = "dev"


settings = Settings()
