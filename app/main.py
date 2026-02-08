"""
Support Tickets Bot — Точка входа.
Бренд: Вячеслав Ветошкин (https://1vetoshkin.ru)
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

# Импорт конфигурации (валидирует BOT_TOKEN при импорте)
from app.config import BOT_TOKEN, LOG_LEVEL
from app.database import init_db
from app.handlers.feature import router as feature_router

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Подключение роутеров
dp.include_router(feature_router)


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    """Обработчик команды /start."""
    await message.answer(
        "👋 Привет! Я бот Support Tickets под брендом Вячеслав Ветошкин.\n\n"
        "📝 Напиши свою проблему — я создам тикет.\n"
        "📋 Команда /help покажет все возможности."
    )


async def main() -> None:
    """Запуск бота."""
    logger.info("🚀 Запуск Support Tickets Bot...")
    
    # Инициализация базы данных
    await init_db()
    
    # Запуск polling
    logger.info("✅ Бот готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
