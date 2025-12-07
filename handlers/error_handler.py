from loguru import logger
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f'Exception while handling an update: {context.error}')

    if isinstance(context.error, TelegramError):
        if 'Timed out' in str(context.error):
            logger.warning('Request timed out')
        elif 'Conflict' in str(context.error):
            logger.warning('Bot token conflict - another instance might be running')

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                '❌ Произошла ошибка при обработке вашего запроса. '
                'Пожалуйста, попробуйте позже.'
            )
        except Exception as e:
            logger.error(f'Failed to send error message: {e}')
