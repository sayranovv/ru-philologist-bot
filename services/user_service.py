from datetime import datetime, timedelta
from typing import List

from sqlalchemy import desc

from models.database import UserQuery, get_session


async def save_query(
        user_id: int,
        command: str,
        query_text: str,
        response_text: str
) -> None:
    session = get_session()
    try:
        new_query = UserQuery(
            user_id=user_id,
            command=command,
            query_text=query_text,
            response_text=response_text[:500],
        )
        session.add(new_query)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_user_history(user_id: int, limit: int = 10) -> List[tuple]:
    session = get_session()
    try:
        queries = session.query(UserQuery).filter(
            UserQuery.user_id == user_id
        ).order_by(
            desc(UserQuery.created_at)
        ).limit(limit).all()

        history = [
            (q.command, q.query_text, q.created_at.strftime('%d.%m %H:%M'))
            for q in queries
        ]
        return history
    except Exception:
        return []
    finally:
        session.close()


async def clear_user_history(user_id: int) -> int:
    session = get_session()
    try:
        count = session.query(UserQuery).filter(
            UserQuery.user_id == user_id
        ).delete()
        session.commit()
        return count
    except Exception:
        session.rollback()
        return 0
    finally:
        session.close()


async def get_user_query_count(user_id: int, minutes: int = 1) -> int:
    session = get_session()
    try:
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        count = session.query(UserQuery).filter(
            UserQuery.user_id == user_id,
            UserQuery.created_at >= time_threshold
        ).count()
        return count
    except Exception:
        return 0
    finally:
        session.close()


async def format_history(history: List[tuple]) -> str:
    if not history:
        return '📭 История запросов пуста'

    result = '📜 Ваша история запросов (последние 10):\n\n'

    for i, (command, query, timestamp) in enumerate(history, 1):
        query_preview = query[:40] + '...' if len(query) > 40 else query
        result += f'{i}. {command} — "{query_preview}"\n   🕐 {timestamp}\n\n'

    return result
