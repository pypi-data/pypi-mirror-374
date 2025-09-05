import os.path
from enum import StrEnum
from pathlib import Path
from typing import Union, Optional
from loguru import logger

from pydantic import Field
from pydantic_settings import BaseSettings

from chef.frontend import get_default_frontend_path

HOME_DIR = Path.home() / '.chef'


class StorageType(StrEnum):
    LOCAL = 'LOCAL'


class ImageFormat(StrEnum):
    AVIF = 'AVIF'


class Settings(BaseSettings):
    """Default config will store all user data in ~/.chef"""
    serve_frontend_path: Union[str, None] = Field(default_factory=get_default_frontend_path)
    serve_frontend: bool = True
    serve_static: bool = True
    database_uri: str = "sqlite:///" + os.path.join(HOME_DIR,  "chef.db")
    log_file: Union[str, None] = None
    log_level: str = "DEBUG"
    log_sql: bool = False

    storage_backend: StorageType = StorageType.LOCAL
    images_folder: str = os.path.join(HOME_DIR,  "images")

    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000

    public_url: str = "http://localhost:8000"
    gpt_enpoint_url: str = "http://localhost:8001"

    sentry_dsn: Optional[str] = None


settings = Settings(_env_file=".env")
