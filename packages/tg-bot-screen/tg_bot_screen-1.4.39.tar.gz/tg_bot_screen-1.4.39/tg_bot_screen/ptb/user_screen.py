from asyncio import gather
from telegram import Bot

from ..screen import ReadyScreen
from .screen import SentScreen
from ..user_data import UserData
from ..user_screen import UserScreen as BaseUserScreen
from .messages.message import SentMessage, Message

class UserScreen(BaseUserScreen):
    def __init__(self, user_data: UserData, bot: Bot):
        super().__init__(user_data)
        self.bot = bot
    
    async def clear(self, user_id: int, delete_messages: bool = True):
        user_data = self.user_data.get(user_id)
        screen = user_data.screen
        if screen and delete_messages:
            await screen.delete(self.bot)
        user_data.screen = None
    
    async def set(self, user_id: int, new_screen: ReadyScreen = None):
        if new_screen == None:
            new_screen = ReadyScreen()
        mapping = self._map_callback_data(user_id, new_screen)
        
        old_screen = self.get(user_id)
        user_data = self.user_data.get(user_id)
        delete, edit, send = self.calc_screen_difference(
            old_screen, new_screen, 
            Message, SentMessage)
        
        new_screen = SentScreen()
        tasks = []
        for message in delete:
            tasks.append( message.delete(self.bot) )
            
        for old_message, new_message in edit:
            transformed_message = new_message.transform(old_message)
            tasks.append( transformed_message.edit(self.bot, mapping) )
            new_screen.extend([transformed_message])
        
        for message in send:
            new_message = await message.send(user_id, self.bot, mapping)
            new_screen.extend([new_message])
            
        await gather(*tasks)
        
        user_data.screen = new_screen
    
    async def buffer(self, user_id: int):
        user_data = self.user_data.get(user_id)
        unsent = None
        if user_data.screen:
            unsent = user_data.screen.get_unsent()
            await user_data.screen.delete(self.bot)
        user_data.screen_buffer = unsent
        user_data.screen = None
        