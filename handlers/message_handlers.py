from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import MAX_MESSAGE_LENGTH, MAX_REQUESTS_PER_MINUTE
from services.llm_service import generate_examples, format_examples
from services.nlp_service import analyze_word, get_word_variations
from services.spell_check_service import check_spelling, format_spell_check_result
from services.user_service import save_query, get_user_query_count


async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            '❌ Пожалуйста, укажите слово для анализа:\n/analyze <слово>'
        )
        return

    query_count = await get_user_query_count(user_id, minutes=1)
    if query_count > MAX_REQUESTS_PER_MINUTE:
        await update.message.reply_text(
            f'⚠️ Вы превысили лимит запросов ({MAX_REQUESTS_PER_MINUTE}/мин). '
            'Повторите позже.'
        )
        return

    word = ' '.join(context.args).strip()

    if len(word) > MAX_MESSAGE_LENGTH:
        await update.message.reply_text(
            f'❌ Слово слишком длинное (макс {MAX_MESSAGE_LENGTH} символов)'
        )
        return

    try:
        analysis = await analyze_word(word)
        variations = await get_word_variations(word)

        response = f'''📖 Анализ слова: "{word}"

🔤 Нормальная форма: {analysis['normal_form']}
📋 Часть речи: {analysis['pos']}
📝 Морфологические признаки: {analysis['grammemes']}

📚 Формы слова:
• Именительный: {', '.join(variations['nominative'])}
• Родительный: {', '.join(variations['genitive'])}
• Дательный: {', '.join(variations['dative'])}
• Винительный: {', '.join(variations['accusative'])}
• Творительный: {', '.join(variations['instrumental'])}
• Предложный: {', '.join(variations['prepositional'])}
'''

        await save_query(user_id, '/analyze', word, response)
        await update.message.reply_text(response)
        logger.info(f'User {user_id} analyzed word: {word}')

    except Exception as e:
        error_msg = f'❌ Ошибка при анализе: {str(e)}'
        await update.message.reply_text(error_msg)
        logger.error(f'Error analyzing word for user {user_id}: {e}')


async def handle_spell_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            '❌ Пожалуйста, укажите текст для проверки:\n/spell_check <текст>'
        )
        return

    query_count = await get_user_query_count(user_id, minutes=1)
    if query_count > MAX_REQUESTS_PER_MINUTE:
        await update.message.reply_text(
            f'⚠️ Вы превысили лимит запросов ({MAX_REQUESTS_PER_MINUTE}/мин). '
            'Повторите позже.'
        )
        return

    text = ' '.join(context.args).strip()

    if len(text) > MAX_MESSAGE_LENGTH:
        await update.message.reply_text(
            f'❌ Текст слишком длинный (макс {MAX_MESSAGE_LENGTH} символов)'
        )
        return

    try:
        await update.message.chat.send_action('typing')
        errors = await check_spelling(text)
        response = await format_spell_check_result(errors)

        await save_query(user_id, '/spell_check', text, response)
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        logger.info(f'User {user_id} checked spelling')

    except Exception as e:
        error_msg = f'❌ Ошибка при проверке орфографии: {str(e)}'
        await update.message.reply_text(error_msg)
        logger.error(f'Error in spell check for user {user_id}: {e}')


async def handle_examples(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            '❌ Пожалуйста, укажите слово:\n/examples <слово>'
        )
        return

    query_count = await get_user_query_count(user_id, minutes=1)
    if query_count > MAX_REQUESTS_PER_MINUTE:
        await update.message.reply_text(
            f'⚠️ Вы превысили лимит запросов ({MAX_REQUESTS_PER_MINUTE}/мин). '
            'Повторите позже.'
        )
        return

    word = ' '.join(context.args).strip()

    if len(word) > MAX_MESSAGE_LENGTH:
        await update.message.reply_text(
            f'❌ Слово слишком длинное (макс {MAX_MESSAGE_LENGTH} символов)'
        )
        return

    try:
        await update.message.chat.send_action('typing')
        examples = await generate_examples(word, count=3)

        if examples is None:
            response = '⚠️ Генерация примеров недоступна (нет API ключа OpenAI)'
        else:
            response = await format_examples(word, examples)

        await save_query(user_id, '/examples', word, response)
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        logger.info(f'User {user_id} requested examples for: {word}')

    except Exception as e:
        error_msg = f'❌ Ошибка при генерации примеров: {str(e)}'
        await update.message.reply_text(error_msg)
        logger.error(f'Error generating examples for user {user_id}: {e}')
