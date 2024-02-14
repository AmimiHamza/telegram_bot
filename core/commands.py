from telegram import Update
from telegram.ext import ContextTypes
import argparse
from .db import AgentDB
from .services import get_study_material_links
from .exceptions import StudyMaterialNotFound

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

        # Parse incoming message
        incoming_message: str = update.message.text
        command_args = incoming_message.split()[1:]

        if len(command_args) == 0:
            # TODO: Reply with a summary of the get command
            await update.message.reply_text('DEFAULT_GET_COMMAND_SUMMARY')
            return
        
        # Parse command and extract arguments
        parsed_args = parser.parse_known_args(command_args)[0]
        course_name = parsed_args.course_name.upper()
        course_type = parsed_args.course_type.upper()
        year = parsed_args.y
        part = parsed_args.p

        # Get and send study material links
        try:
            links = get_study_material_links(self.db, course_name, course_type, year, part)
            for link in links:
                await update.message.reply_text(link)
        except StudyMaterialNotFound as e:
            await update.message.reply_text(str(e))
        

        
        
        
        
        

                

            