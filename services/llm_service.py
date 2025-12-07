from typing import Optional, List

from gigachat import GigaChat
from loguru import logger

from config import GIGACHAT_CREDENTIALS


async def generate_examples(word: str, count: int = 3) -> Optional[List[str]]:
    if not GIGACHAT_CREDENTIALS:
        logger.warning("GIGACHAT_CREDENTIALS not set")
        return None

    try:
        async with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False,
                            scope="GIGACHAT_API_PERS") as giga:

            prompt = (
                f'Придумай {count} предложения со словом "{word}". '
                'Каждое предложение должно быть с новой строки и начинаться с цифры. '
                'Не пиши никакого вводного текста, только сами предложения.'
            )

            response = await giga.achat(prompt)

            content = response.choices[0].message.content

            examples = [line.strip() for line in content.split('\n') if line.strip()]

            logger.info(f"GigaChat generated {len(examples)} examples for word '{word}'")
            return examples

    except Exception as e:
        logger.error(f"GigaChat API error: {e}")
        return None


async def format_examples(word: str, examples: list) -> str:
    if not examples:
        return f'❌ Не удалось сгенерировать примеры для слова "{word}" (возможно, проблема с токеном или API)'

    result = f'📝 <b>Примеры использования слова "{word}":</b>\n\n'

    for i, example in enumerate(examples[:5]):
        if example[0].isdigit():
            result += f'{example}\n'
        else:
            result += f'{i + 1}. {example}\n'

    return result
