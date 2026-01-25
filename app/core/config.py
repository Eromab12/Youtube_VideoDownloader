import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración global de la aplicación usando Pydantic.
    Las variables pueden ser sobreescritas por variables de entorno (.env).
    """
    PROJECT_NAME: str = "YTDL-NIS Python"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    
    # Directorio donde se guardarán los archivos descargados.
    # Se usa os.path.join para compatibilidad entre Windows/Linux.
    DOWNLOAD_DIR: str = os.path.join(os.getcwd(), "media")
    
    # URL de conexión a la base de datos (SQLite asíncrono por defecto)
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"

    class Config:
        """Configuración interna de Pydantic."""
        case_sensitive = True
        env_file = ".env" # Carga variables desde archivo .env si existe

@lru_cache()
def get_settings():
    """
    Retorna una instancia de Settings cacheada.
    Esto evita leer el archivo .env en cada llamada, mejorando el rendimiento.
    """
    return Settings()

settings = get_settings()

# Verificación inicial: Crear directorio de descargas si no existe
if not os.path.exists(settings.DOWNLOAD_DIR):
    os.makedirs(settings.DOWNLOAD_DIR)
