"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import sys

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
async def temp_db():
    """Create temporary database for testing."""
    from app.database.db import set_db_path, init_db
    
    # Создаём временный файл для БД
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = Path(f.name)
    
    # Устанавливаем путь к тестовой БД
    set_db_path(db_path)
    
    # Инициализируем БД
    await init_db()
    
    yield db_path
    
    # Очистка
    set_db_path(None)
    if db_path.exists():
        db_path.unlink()
