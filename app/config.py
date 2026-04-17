from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    database_url: str = "sqlite:///./chefbot_api.db"  # SQLite para desarrollo local
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_name: str = "ChefBot API"
    debug: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
