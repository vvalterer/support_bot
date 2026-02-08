"""
Централизованная конфигурация приложения.
Загружает переменные окружения и валидирует их.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_env(key: str, default: str | None = None, required: bool = False) -> str | None:
    """Получить переменную окружения с валидацией."""
    value = os.getenv(key, default)
    if required and not value:
        logging.critical(f"❌ Обязательная переменная {key} не установлена!")
        sys.exit(1)
    return value


# === Обязательные переменные ===
BOT_TOKEN: str = get_env("BOT_TOKEN", required=True)

# === Опциональные переменные ===
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in get_env("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

DB_PATH: Path = BASE_DIR / get_env("DB_PATH", "data/database.sqlite3")
LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")

# Создаём папку для БД если не существует
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
