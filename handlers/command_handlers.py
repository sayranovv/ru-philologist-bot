from telegram import Update
from telegram.ext import ContextTypes

from services.user_service import save_query, format_history, get_user_history

HELP_TEXT = '''Я ассистент по анализу русского языка! 📚

Доступные команды:

/start — начать работу
/help — справка
/analyze <слово> — морфологический анализ слова
/spell_check <текст> — проверка орфографии
/examples <слово> — примеры использования слова
/history — просмотр ваших запросов
/clear_history — удалить историю

Примеры использования:
/analyze книга
/spell_check Это написано корректна
/examples красивый
'''

START_TEXT = '''Привет! 👋 Я "Русский Филолог" — ваш ассистент по анализу текстов на русском языке!

Я умею:
✨ Разбирать слова по частям речи
✨ Проверять орфографию и грамматику
✨ Генерировать примеры предложений
✨ Хранить историю ваших запросов

Введите /help для справки по командам!
'''


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await save_query(user_id, '/start', '', START_TEXT)
    await update.message.reply_text(START_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await save_query(user_id, '/help', '', HELP_TEXT)
    await update.message.reply_text(HELP_TEXT)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    history = await get_user_history(user_id, limit=10)
    response = await format_history(history)
    await save_query(user_id, '/history', '', response)
    await update.message.reply_text(response)


async def clear_history_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    from services.user_service import clear_user_history

    user_id = update.effective_user.id
    count = await clear_user_history(user_id)
    response = f'✅ История очищена! Удалено {count} записей.'
    await save_query(user_id, '/clear_history', '', response)
    await update.message.reply_text(response)
