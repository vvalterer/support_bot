"""
Хэндлеры для работы с тикетами.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.database import create_ticket, get_user_tickets, close_ticket

logger = logging.getLogger(__name__)
router = Router(name=__name__)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои тикеты", callback_data="my_tickets")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])


@router.message(F.text == "/help")
async def help_cmd(message: Message) -> None:
    """Вывод справки."""
    await message.answer(
        "🤖 <b>Support Tickets Bot</b>\n\n"
        "📝 Напишите проблему — создам тикет\n"
        "📋 <b>мои тикеты</b> — список ваших тикетов\n"
        "✅ <b>закрыть #1</b> — закрыть тикет по номеру\n\n"
        "💡 Тикеты сохраняются даже после перезапуска бота!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    """Справка через кнопку."""
    await callback.message.answer(
        "🤖 <b>Support Tickets Bot</b>\n\n"
        "📝 Напишите проблему — создам тикет\n"
        "📋 <b>мои тикеты</b> — список ваших тикетов\n"
        "✅ <b>закрыть #1</b> — закрыть тикет по номеру",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "my_tickets")
async def my_tickets_callback(callback: CallbackQuery) -> None:
    """Список тикетов через кнопку."""
    tickets = await get_user_tickets(callback.from_user.id)
    
    if not tickets:
        await callback.message.answer("📭 У вас пока нет тикетов.", reply_markup=get_main_keyboard())
        await callback.answer()
        return
    
    lines = []
    keyboard_buttons = []
    for t in tickets:
        status_emoji = "🟢" if t.status == "new" else "⚫"
        lines.append(f"{status_emoji} <b>#{t.id}</b> — {t.status}\n   {t.text[:50]}{'...' if len(t.text) > 50 else ''}")
        if t.status == "new":
            keyboard_buttons.append([InlineKeyboardButton(text=f"❌ Закрыть #{t.id}", callback_data=f"close_{t.id}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="help")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = "📋 <b>Ваши тикеты:</b>\n\n" + "\n\n".join(lines)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("close_"))
async def close_ticket_callback(callback: CallbackQuery) -> None:
    """Закрытие тикета через кнопку."""
    ticket_id = int(callback.data.split("_")[1])
    success = await close_ticket(ticket_id, callback.from_user.id)
    
    if success:
        await callback.message.answer(f"✅ Тикет #{ticket_id} закрыт.", reply_markup=get_main_keyboard())
    else:
        await callback.message.answer(f"❌ Не удалось закрыть тикет #{ticket_id}.", reply_markup=get_main_keyboard())
    await callback.answer()


@router.message(F.text.lower().startswith("закрыть #"))
async def close_ticket_handler(message: Message) -> None:
    """Закрытие тикета по ID."""
    try:
        ticket_id = int(message.text.split("#", 1)[1].strip())
        success = await close_ticket(ticket_id, message.from_user.id)
        
        if success:
            await message.answer(f"✅ Тикет #{ticket_id} закрыт.", reply_markup=get_main_keyboard())
        else:
            await message.answer(f"❌ Тикет #{ticket_id} не найден или не принадлежит вам.")
    except ValueError:
        await message.answer("⚠️ Неверный формат. Используйте: <code>закрыть #1</code>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка при закрытии тикета: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@router.message(F.text.lower().in_({"мои тикеты", "мои", "тикеты", "список"}))
async def my_tickets_handler(message: Message) -> None:
    """Список тикетов пользователя."""
    tickets = await get_user_tickets(message.from_user.id)
    
    if not tickets:
        await message.answer("📭 У вас пока нет тикетов.", reply_markup=get_main_keyboard())
        return
    
    lines = []
    keyboard_buttons = []
    for t in tickets:
        status_emoji = "🟢" if t.status == "new" else "⚫"
        lines.append(f"{status_emoji} <b>#{t.id}</b> — {t.status}\n   {t.text[:50]}{'...' if len(t.text) > 50 else ''}")
        if t.status == "new":
            keyboard_buttons.append([InlineKeyboardButton(text=f"❌ Закрыть #{t.id}", callback_data=f"close_{t.id}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="help")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    text = "📋 <b>Ваши тикеты:</b>\n\n" + "\n\n".join(lines)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.message()
async def new_ticket_handler(message: Message) -> None:
    """Создание нового тикета из любого сообщения."""
    if message.text and message.text.startswith("/"):
        await message.answer("❓ Неизвестная команда. Напишите /help для справки.", reply_markup=get_main_keyboard())
        return
    
    ticket = await create_ticket(
        user_id=message.from_user.id,
        text=message.text or "[медиа-сообщение]"
    )
    
    await message.answer(
        f"✅ Создан тикет <b>#{ticket.id}</b>\n"
        f"📊 Статус: <code>{ticket.status}</code>\n\n"
        "Мы свяжемся с вами в ближайшее время!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
