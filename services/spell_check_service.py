import re
from typing import List, Dict, Any

from loguru import logger
from spellchecker import SpellChecker

spell = SpellChecker(language='ru')

spell.word_frequency.load_words(['чат-бот', 'телеграм', 'онлайн', 'веб'])


async def check_spelling(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    words_in_text = re.findall(r'[а-яА-ЯёЁ]{2,}', text)

    if not words_in_text:
        return []

    errors = []

    unknown_words = spell.unknown(words_in_text)

    logger.info(f"Checking text: '{text[:50]}...'. Found unknown words: {unknown_words}")

    for word in unknown_words:
        candidates = spell.candidates(word)

        pos = text.find(word)

        error_entry = {
            'word': word,
            's': list(candidates) if candidates else [],
            'pos': pos,
            'len': len(word),
            'code': 1
        }
        errors.append(error_entry)

    errors.sort(key=lambda x: x['pos'])

    return errors


async def format_spell_check_result(errors: List[Dict[str, Any]]) -> str:
    if not errors:
        return '✅ Текст не содержит ошибок (или все слова есть в словаре)!'

    result = '❌ Найдены возможные ошибки:\n\n'

    for i, error in enumerate(errors[:10], 1):
        word = error.get('word', '')
        suggestions = error.get('s', [])

        result += f'{i}. <b>{word}</b>'

        if suggestions:
            top_suggestions = list(suggestions)[:5]
            suggestions_str = ', '.join([f'<i>{s}</i>' for s in top_suggestions])
            result += f'\n   Варианты: {suggestions_str}'

        result += '\n\n'

    if len(errors) > 10:
        result += f'... и ещё {len(errors) - 10} слов'

    return result
