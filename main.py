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
    await update.message.reply_text('you can use:\nGET ELEMENT TYPE INDEX :for getting files\nSHOW ELEMENT TYPE :for listing the files names in the bot\nELEMENT can be like java ,TG...\nTYPE can be cours exam or td\nINDEX can be like 1 2 or 2022 for example')

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
    elif text[0] not in commands:
        response: str = f"la commande '{text[0]}' n'existe pas f had lbot"
    elif text[0] == 'get' and len(text) in [3,4]:
        course_name, course_type= text[1], text[2]
        indice=text[3] if len(text)==4 else '%'
        response=await get_pdf(course_name,course_type,indice,sender_id,context)
    elif text[0]=='show' and len(text)<4:
        course_name=text[1] if len(text)==2 else '%'
        course_type=text[2] if len(text)==3 else '%'
        await show_names(course_name,course_type,update)
        response=""
    elif  text[0]=='add' and sender_id in administateurs:
        course_name, course_type,index,url= text[1], text[2],text[3],text[4]
        response=await add_to_db(course_name,course_type,index,url,update)
    else:
        response: str = "Invalid Syntax"
    print('Bot:', response)
    await update.message.reply_text(response)

async def add_to_db(course_name,course_type,index,url,update: Update):
    # Connect to SQLite DB
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (url,element,type,indice,state) VALUES (?,?,?,?,?)", (url, course_name, course_type, index,1))
    conn.commit()
    conn.close()
    response='le pdf est ajouté à la base de données.'
    return response
async def show_names(course_name,course_type,update: Update):
    # Connect to SQLite DB
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT element || ' ' || type || ' ' || indice AS course_info FROM courses WHERE element LIKE ? AND type LIKE ? AND state = 1", (course_name, course_type))
    result = cursor.fetchall()
    conn.close()
    # Check result and respond
    if result:
        for response in result:
            await update.message.reply_text(response[0])
    else:
        response="n'existe pas"
        await update.message.reply_text(response)
    
    return ''

async def get_pdf(course_name,course_type,indice,sender_id,context: ContextTypes.DEFAULT_TYPE):
    # Connect to SQLite DB
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM courses WHERE element = ? AND type = ? AND indice LIKE ? AND state = 1", (course_name, course_type, indice))
    result = cursor.fetchall()
    conn.close()
    # Check result and respond
    if result:
        for File_URL in result:
            await context.bot.send_document(chat_id=sender_id, document=File_URL[0])
            response = "here is ur pdf ^_^"
    else:
        response = "Not found 🙄"
    return response

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
