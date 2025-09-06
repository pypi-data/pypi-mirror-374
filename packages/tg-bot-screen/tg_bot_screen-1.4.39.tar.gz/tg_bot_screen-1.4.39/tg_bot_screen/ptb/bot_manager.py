from telegram import Update, Bot
from telegram import Message as TgMessage
from telegram.ext import Application, CallbackQueryHandler, MessageHandler

from ..bot_manager import BotManager as BaseBotManager
from .user_screen import UserScreen
from ..user_data import UserDataManager

class BotManager(BaseBotManager):
    def __init__(self, application: Application):
        super().__init__()
        self.bot: Bot = application.bot
        self.application = application
    
    def build(self):
        user_data = UserDataManager()
        screen = UserScreen(user_data, self.bot)
        self.system_user_data = user_data
        self.screen = screen
        return self
    
    def get_callback_query_handler(self):
        async def callback(update: Update, context):
            user_id = update.callback_query.from_user.id
            query_data = update.callback_query.data
            await self._handle_callback_query(user_id, query_data, 
                update=update, context=context)
            await update.callback_query.answer()
        return CallbackQueryHandler(callback)

    def get_message_handler(self):
        async def callback(update: Update, context):
            user_id = update.message.from_user.id
            await self._handle_message(user_id, update=update
                , message=update.message, context=context)
            
        return MessageHandler(None, callback)
    
    async def delete_message(self, message: TgMessage, **kwargs):
        await message.delete()
    
    def add_handlers(self):
        """Эта функция должна вызываться ПОСЛЕ 
        регистрации /start или подобных команд"""
        self.application.add_handlers([
            self.get_callback_query_handler(),
            self.get_message_handler()
        ])