"""
Тесты для слоя базы данных.
"""
import pytest
from app.database.db import create_ticket, get_user_tickets, close_ticket, get_ticket_by_id


pytestmark = pytest.mark.asyncio


class TestCreateTicket:
    """Тесты создания тикетов."""
    
    async def test_create_ticket_returns_ticket(self, temp_db):
        """Создание тикета возвращает объект Ticket."""
        ticket = await create_ticket(user_id=123, text="Test problem")
        
        assert ticket.id == 1
        assert ticket.user_id == 123
        assert ticket.text == "Test problem"
        assert ticket.status == "new"
    
    async def test_create_multiple_tickets_increments_id(self, temp_db):
        """ID тикетов увеличивается."""
        t1 = await create_ticket(user_id=123, text="First")
        t2 = await create_ticket(user_id=123, text="Second")
        t3 = await create_ticket(user_id=456, text="Third")
        
        assert t1.id == 1
        assert t2.id == 2
        assert t3.id == 3


class TestGetUserTickets:
    """Тесты получения тикетов пользователя."""
    
    async def test_get_empty_list_for_new_user(self, temp_db):
        """Пустой список для нового пользователя."""
        tickets = await get_user_tickets(user_id=999)
        
        assert tickets == []
    
    async def test_get_only_user_tickets(self, temp_db):
        """Возвращаются только тикеты указанного пользователя."""
        await create_ticket(user_id=111, text="User 111 ticket")
        await create_ticket(user_id=222, text="User 222 ticket")
        await create_ticket(user_id=111, text="Another 111 ticket")
        
        tickets = await get_user_tickets(user_id=111)
        
        assert len(tickets) == 2
        assert all(t.user_id == 111 for t in tickets)


class TestCloseTicket:
    """Тесты закрытия тикетов."""
    
    async def test_close_own_ticket_succeeds(self, temp_db):
        """Пользователь может закрыть свой тикет."""
        ticket = await create_ticket(user_id=123, text="My ticket")
        
        result = await close_ticket(ticket.id, user_id=123)
        
        assert result is True
        
        # Проверяем статус
        updated = await get_ticket_by_id(ticket.id)
        assert updated.status == "closed"
    
    async def test_close_other_user_ticket_fails(self, temp_db):
        """Нельзя закрыть чужой тикет."""
        ticket = await create_ticket(user_id=123, text="Not yours")
        
        result = await close_ticket(ticket.id, user_id=999)
        
        assert result is False
        
        # Статус не изменился
        updated = await get_ticket_by_id(ticket.id)
        assert updated.status == "new"
    
    async def test_close_nonexistent_ticket_fails(self, temp_db):
        """Закрытие несуществующего тикета возвращает False."""
        result = await close_ticket(ticket_id=9999, user_id=123)
        
        assert result is False


class TestGetTicketById:
    """Тесты получения тикета по ID."""
    
    async def test_get_existing_ticket(self, temp_db):
        """Получение существующего тикета."""
        created = await create_ticket(user_id=123, text="Find me")
        
        ticket = await get_ticket_by_id(created.id)
        
        assert ticket is not None
        assert ticket.text == "Find me"
    
    async def test_get_nonexistent_returns_none(self, temp_db):
        """Несуществующий тикет возвращает None."""
        ticket = await get_ticket_by_id(9999)
        
        assert ticket is None
