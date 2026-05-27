from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{(DATA_DIR / 'vault.db').as_posix()}"
    session_ttl_minutes: int = 15

    enable_hibp_range_api: bool = True
    hibp_range_base_url: str = "https://api.pwnedpasswords.com/range/"
    hibp_user_agent: str = "PasswordManagerMVP (educational)"


settings = Settings()