from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
from constents import *
import sqlite3

TABLE='courses' #the data base will change from a group to another.

dbname=f"{TABLE}.db"
conn = sqlite3.connect(dbname)
cursor = conn.cursor()

# Creat the database
query=f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        element TEXT NOT NULL,
        type TEXT NOT NULL,
        indice TEXT NOT NULL,
        state INTEGER NOT NULL);"""
cursor.execute(query)
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
        print('waaaaaaaaaaaaa')
        indice=text[3] if len(text)==4 else '%'
        response=await get_pdf(course_name,course_type,indice,sender_id,context)
    elif text[0]=='show' and len(text)<4:
        course_name=text[1] if len(text)==2 else '%'
        course_type=text[2] if len(text)==3 else '%'
        await show_names(course_name,course_type,update)
        response=""
    elif  text[0]=='add' and sender_id in administateurs:
        course_name, course_type,index,url= text[1], text[2],text[3],text[4]
        response=await add_to_db(course_name,course_type,index,url)
    elif  text[0]=='delete' and sender_id in administateurs:
        course_name= text[1] if len(text)==2 else '%'
        course_type=text[2] if len(text)==3 else '%'
        index=text[3] if len(text)==4 else '%'
        response=await delete_from_db(course_name,course_type,index)
    elif  text[0]=='update' and sender_id in administateurs:
        course_name, course_type,index,url= text[1], text[2],text[3],text[4]
        await delete_from_db(course_name,course_type,index)
        await add_to_db(course_name,course_type,index,url)
        response=f'the url of {course_name}-{course_type}-{index} has been updated.'
    else:
        response: str = "Invalid Syntax"
    print('Bot:', response)
    await update.message.reply_text(response)

async def add_to_db(course_name,course_type,index,url):
    # Connect to SQLite DB
    dbname=f"{TABLE}.db"
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    print(course_name)
    query=f"INSERT INTO {TABLE} (url,element,type,indice,state) VALUES (?,?,?,?,?)"
    print(query)
    cursor.execute(query, (url, course_name, course_type, index,1))
    conn.commit()
    conn.close()
    response='le pdf est ajouté à la base de données.'
    return response

async def delete_from_db(course_name,course_type,index):
    # Connect to SQLite DB
    dbname=f"{TABLE}.db"
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    query=f"DELETE FROM {TABLE} WHERE element LIKE ? AND type LIKE ? AND indice LIKE ? AND state=?"
    cursor.execute(query, (course_name, course_type, index,1))
    conn.commit()
    conn.close()
    response='le pdf est supprimé de la base de données.'
    return response
async def show_names(course_name,course_type,update: Update):
    # Connect to SQLite DB
    dbname=f"{TABLE}.db"
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    query=f"SELECT element || ' ' || type || ' ' || indice AS course_info FROM {TABLE} WHERE element LIKE ? AND type LIKE ? AND state = 1 ORDER BY element ASC"
    cursor.execute(query, (course_name, course_type))
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
    print(course_name)
    # Connect to SQLite DB
    dbname=f"{TABLE}.db"
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    query=f"SELECT url FROM {TABLE} WHERE element = ? AND type = ? AND indice LIKE ? AND state = 1"
    cursor.execute(query, (course_name, course_type, indice))
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
