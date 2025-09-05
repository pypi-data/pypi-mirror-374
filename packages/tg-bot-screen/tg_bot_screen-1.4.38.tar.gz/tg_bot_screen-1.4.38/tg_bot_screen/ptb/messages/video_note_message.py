from telegram import Message as PTBMessage
from ...message import VideoNoteMessage as BaseVideoNoteMessage
from ...message import SentVideoNoteMessage as BaseSentVideoNoteMessage
from .message import HasButtonRows, Message, SentMessage

class VideoNoteMessage(BaseVideoNoteMessage, Message): ...

class SentVideoNoteMessage(BaseSentVideoNoteMessage, SentMessage): ...