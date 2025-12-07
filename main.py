import asyncio
import signal
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from loguru import logger
import sys
from models.database import init_db
from handlers.command_handlers import (
    start_command,
    help_command,
    history_command,
    clear_history_command,
)
from handlers.message_handlers import (
    handle_analyze,
    handle_spell_check,
    handle_examples,
)
from handlers.error_handler import error_handler


logger.remove()
logger.add(
    sys.stdout,
    format='<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> '
           '- <level>{message}</level>',
    level=LOG_LEVEL,
)
logger.add(
    'logs/bot.log',
    rotation='500 MB',
    level=LOG_LEVEL,
    format='{time} | {level: <8} | {name}:{function} - {message}',
)


class BotApplication:
    def __init__(self) -> None:
        self.app: Application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
        
    def setup_handlers(self) -> None:
        self.app.add_handler(CommandHandler('start', start_command))
        self.app.add_handler(CommandHandler('help', help_command))
        self.app.add_handler(CommandHandler('analyze', handle_analyze))
        self.app.add_handler(CommandHandler('spell_check', handle_spell_check))
        self.app.add_handler(CommandHandler('examples', handle_examples))
        self.app.add_handler(CommandHandler('history', history_command))
        self.app.add_handler(CommandHandler('clear_history', clear_history_command))
        
        self.app.add_error_handler(error_handler)
    
    async def start(self) -> None:
        logger.info('Initializing database...')
        init_db()
        logger.info('Database initialized successfully')
        
        logger.info('Starting bot...')
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=['message', 'my_chat_member'])
        logger.info('Bot started successfully and polling for updates')
        
    async def stop(self) -> None:
        logger.info('Shutting down bot...')
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
        logger.info('Bot stopped')


async def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error('TELEGRAM_BOT_TOKEN not set in .env file')
        sys.exit(1)
    
    bot_app = BotApplication()
    
    def signal_handler(sig, frame) -> None:
        logger.info(f'Received signal {sig}, shutting down gracefully...')
        asyncio.create_task(bot_app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await bot_app.start()
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        await bot_app.stop()
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        await bot_app.stop()
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot terminated')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        sys.exit(1)
