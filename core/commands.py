from telegram import Update
from telegram.ext import ContextTypes
import argparse
from .db import AgentDB
from .services import get_study_material_links
from .exceptions import StudyMaterialNotFound
from .constants import HELP_COMMAND_SUMMARY, GET_COMMAND_SUMMARY, BOT_INTRODUCTION_MESSAGE, BOT_USERNAME, GREETING

class BotCommand:
    def __init__(self,db_url: str):
        self.db = AgentDB(db_url)

    async def get(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Init command parser
        parser = argparse.ArgumentParser()
        parser.add_argument('course_name', help='Name of the course')
        parser.add_argument('course_type', help='Type of the course')
        parser.add_argument('-p', help='Part', type=int)
        parser.add_argument('-y', help='Year', type=int)
        parser.add_argument('-s', help='Year', type=str)

        # Parse incoming message
        incoming_message: str = update.message.text
        command_args = incoming_message.split()[1:]

        #FIX: Consider the case where the user sends the request in a group
        if len(command_args) == 0:
            # TODO: Reply with a summary of the get command
            await update.message.reply_text(GET_COMMAND_SUMMARY)
            return
        
        # Parse command and extract arguments
        parsed_args = parser.parse_known_args(command_args)[0]
        course_name = parsed_args.course_name.upper()
        course_type = parsed_args.course_type.upper()
        year = parsed_args.y
        part = parsed_args.p
        session = parsed_args.s.upper() if parsed_args.s is not None else None

        # Get and send study material links
        try:
            links = get_study_material_links(self.db, course_name, course_type, year, part, session)
            for link in links:
                await context.bot.send_document(chat_id=update.message.chat_id, document=link)
        except StudyMaterialNotFound as e:
            await update.message.reply_text(str(e))
        
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(HELP_COMMAND_SUMMARY)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(BOT_INTRODUCTION_MESSAGE)

    async def default(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type: str = update.message.chat.type
        text: str = update.message.text
        sender_id = update.message.chat.id
        sender_username = update.message.chat.username
        print(f'User({update.message.chat.id}) in {message_type}:"{text}"')

        if message_type == 'group':
            if BOT_USERNAME in text:
                text: str = text.replace(BOT_USERNAME, '').strip()
            else:
                return
        
        text=text.lower().split()
        if text[0] in GREETING:
            response: str = f'Hello {sender_username.capitalize()} 👋, How can I assist you today ?'
        await update.message.reply_text(response)


    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} caused {context.error}')



        
        
        
        
        

                

            