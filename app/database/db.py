"""
Асинхронный слой работы с SQLite для хранения тикетов.
"""
import aiosqlite
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Путь к БД (можно переопределить для тестов)
_db_path: Path | None = None


def set_db_path(path: Path) -> None:
    """Установить путь к БД (для тестов)."""
    global _db_path
    _db_path = path


def get_db_path() -> Path:
    """Получить путь к БД."""
    if _db_path:
        return _db_path
    from app.config import DB_PATH
    return DB_PATH


@dataclass
class Ticket:
    """Модель тикета."""
    id: int
    user_id: int
    text: str
    status: str
    created_at: str


async def init_db() -> None:
    """Инициализация базы данных и создание таблиц."""
    db_path = get_db_path()
    logger.info(f"📦 Инициализация БД: {db_path}")
    
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        await db.commit()
    
    logger.info("✅ БД инициализирована")


async def create_ticket(user_id: int, text: str) -> Ticket:
    """Создать новый тикет."""
    async with aiosqlite.connect(get_db_path()) as db:
        cursor = await db.execute(
            "INSERT INTO tickets (user_id, text, status) VALUES (?, ?, 'new')",
            (user_id, text)
        )
        await db.commit()
        ticket_id = cursor.lastrowid
        
        logger.info(f"📝 Создан тикет #{ticket_id} от пользователя {user_id}")
        
        return Ticket(
            id=ticket_id,
            user_id=user_id,
            text=text,
            status="new",
            created_at=datetime.now().isoformat()
        )


async def get_user_tickets(user_id: int) -> list[Ticket]:
    """Получить все тикеты пользователя."""
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, user_id, text, status, created_at FROM tickets WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        
        return [
            Ticket(
                id=row["id"],
                user_id=row["user_id"],
                text=row["text"],
                status=row["status"],
                created_at=row["created_at"]
            )
            for row in rows
        ]


async def get_ticket_by_id(ticket_id: int) -> Optional[Ticket]:
    """Получить тикет по ID."""
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, user_id, text, status, created_at FROM tickets WHERE id = ?",
            (ticket_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return Ticket(
            id=row["id"],
            user_id=row["user_id"],
            text=row["text"],
            status=row["status"],
            created_at=row["created_at"]
        )


async def close_ticket(ticket_id: int, user_id: int) -> bool:
    """
    Закрыть тикет.
    
    Returns:
        True если тикет закрыт, False если не найден или не принадлежит пользователю.
    """
    async with aiosqlite.connect(get_db_path()) as db:
        cursor = await db.execute(
            "UPDATE tickets SET status = 'closed' WHERE id = ? AND user_id = ?",
            (ticket_id, user_id)
        )
        await db.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"✅ Тикет #{ticket_id} закрыт пользователем {user_id}")
            return True
        
        return False
