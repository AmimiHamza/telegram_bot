from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
from dotenv import load_dotenv
import os
from core.commands import BotCommand
from core.utils import get_db_url




if __name__ == '__main__':
    print('Starting...')

    load_dotenv()
    ENV = os.getenv('ENV')
    DB_URL = get_db_url(ENV)
    TOKEN = os.getenv('TOKEN')


    app = Application.builder() \
                     .token(TOKEN) \
                     .build()

    bot = BotCommand(DB_URL)

    # Commands
    app.add_handler(CommandHandler('start', bot.start))
    app.add_handler(CommandHandler('help', bot.help))
    app.add_handler(CommandHandler('get', bot.get))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, bot.default))
    
    # Errors
    app.add_error_handler(bot.error)

    print('Polling...')
    app.run_polling(poll_interval=2)
