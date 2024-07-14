from telegram import Update
from telegram.ext import ContextTypes
import ipaddress
from user_manager import UserManager
from config import MAX_URLS, MAX_IPS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    chat_id = str(update.effective_chat.id)
    user_manager.add_user(chat_id)
    await update.message.reply_text(
        'Welcome to the Power Outage Monitor Bot! Use /set_url to add URLs or /set_ip to add IPv4 address to monitor.')


async def set_identifier(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager, identifier_type: str) -> None:
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            f'Please provide a {identifier_type}. Usage: /set_{identifier_type} <{identifier_type}>')
        return
    identifier = context.args[0]

    if identifier_type == 'ip':
        try:
            ipaddress.ip_address(identifier)
        except ValueError:
            await update.message.reply_text(
                f'IP address {identifier} is not valid. Please provide a valid IPv4 address.')
            return

    if user_manager.add_identifier(chat_id, identifier, f"{identifier_type}s"):
        if len(user_manager.get_identifiers(chat_id, f"{identifier_type}s")) <= (
                MAX_URLS if identifier_type == 'url' else MAX_IPS):
            await update.message.reply_text(f'{identifier_type.upper()} {identifier} has been added to monitoring.')
        else:
            user_manager.delete_identifier(chat_id, identifier, f"{identifier_type}s")
            await update.message.reply_text(
                f'{identifier_type.upper()}s limit is exceeded. You cannot add more than {MAX_URLS if identifier_type == "url" else MAX_IPS} {identifier_type.upper()}s.')
    else:
        await update.message.reply_text(f'{identifier_type.upper()} {identifier} is already being monitored.')


async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await set_identifier(update, context, user_manager, 'url')


async def set_ip(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await set_identifier(update, context, user_manager, 'ip')


async def list_identifiers(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager, identifier_type: str) -> None:
    chat_id = str(update.effective_chat.id)
    identifiers = user_manager.get_identifiers(chat_id, f"{identifier_type}s")
    if identifiers:
        await update.message.reply_text(f'Monitored {identifier_type.upper()}s:\n' + '\n'.join(identifiers))
    else:
        await update.message.reply_text(
            f'No {identifier_type.upper()}s are currently being monitored. Use /set_{identifier_type} to add {identifier_type.upper()}s.')


async def list_urls(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await list_identifiers(update, context, user_manager, 'url')


async def list_ips(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await list_identifiers(update, context, user_manager, 'ip')


async def delete_identifier(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager, identifier_type: str) -> None:
    chat_id = str(update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            f'Please provide a {identifier_type.upper()} to delete. Usage: /delete_{identifier_type} <{identifier_type}>')
        return
    identifier = context.args[0]
    if user_manager.delete_identifier(chat_id, identifier, f"{identifier_type}s"):
        await update.message.reply_text(f'{identifier_type.upper()} {identifier} has been successfully deleted.')
    else:
        await update.message.reply_text(f'{identifier_type.upper()} {identifier} was not found in your monitored list.')


async def delete_url(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await delete_identifier(update, context, user_manager, 'url')


async def delete_ip(update: Update, context: ContextTypes.DEFAULT_TYPE, user_manager: UserManager) -> None:
    await delete_identifier(update, context, user_manager, 'ip')