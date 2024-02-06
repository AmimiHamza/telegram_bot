from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
from constents import *
import sqlite3

conn = sqlite3.connect('courses.db')
cursor = conn.cursor()

# Creat the database
cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        element TEXT NOT NULL,
        type TEXT NOT NULL,
        indice TEXT NOT NULL,
        state INTEGER NOT NULL);""")
conn.close()

# Handle commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, thanks for chatting. This is the bot for DSE students.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please type GET_TYPE_INDEX.')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command.')

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    sender_id = update.message.chat.id
    print(f'User({update.message.chat.id}) in {message_type}:"{text}"')
    response=''
    if message_type == 'group':
        if BOT_USERNAME in text:
            text: str = text.replace(BOT_USERNAME, '').strip()
        else:
            return
    
    text=text.lower().split()
    if text[0] in greeting:
        response: str = 'Helloooooo, how can I assist u'
    elif text[0]!='get':
        response: str = f"la commande '{text[0]}' n'existe pas f had lbot"
    elif text[0] == 'get' and len(text) in [3,4]:
        course_name, course_type= text[1], text[2]
        indice=text[3] if len(text)==4 else '%'
        # Connect to SQLite DB
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM courses WHERE element = ? AND type = ? AND indice LIKE ? AND state = 1", (course_name, course_type, indice))
        result = cursor.fetchall()
        conn.close()
        # Check result and respond
        if result:
            for File_URL in result:
                await send_pdf(sender_id, File_URL[0], context)
                print(File_URL[0])
                response = "here is ur pdf ^_^"
        else:
            response = "Not found 🙄"
    else:
        response: str = "Invalid Syntax"
    print('Bot:', response)
    await update.message.reply_text(response)

async def send_pdf(chat_id, pdf_url, context):
    try:
        await context.bot.send_document(chat_id=chat_id, document=pdf_url)
    except Exception as e:
        print(f"Failed to send PDF: {e}")
# Handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused {context.error}')



if __name__ == '__main__':
    print('Starting...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=2)
