"""Database module for ticket storage."""
from .db import init_db, create_ticket, get_user_tickets, close_ticket, get_ticket_by_id

__all__ = ["init_db", "create_ticket", "get_user_tickets", "close_ticket", "get_ticket_by_id"]
