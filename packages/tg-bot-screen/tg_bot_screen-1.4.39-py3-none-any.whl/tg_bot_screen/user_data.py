from typing import Type, TypeVar
from .error_info import check_bad_value
from .session import InputSession, Session
from .input_callback import InputCallback
from .callback_data import CallbackDataMapping
from .screen import ReadyScreen, SentScreen

SessionType = TypeVar("SessionType")

class UserData:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.callback_mapping = CallbackDataMapping()
        self.media_group_id: str | None = None
        self.input_callback: InputCallback | None = None
        self.directory_stack: list[str] = []
        self.screen: SentScreen | None = None
        self.screen_buffer: ReadyScreen | None = None
        self.__sessions: dict[str, Session] = {}
    
    def reset_input_callback(self):
        self.input_callback = None
    
    @property
    def sessions(self):
        return tuple([ item[1] for item in self.__sessions.items() ])
    
    @property
    def input_sessions(self):
        result: list[InputSession] = []
        for session in self.sessions:
            if isinstance(session, InputSession):
                result.append(session)
        return tuple(result)
    
    def add_session(self, session: Session) -> bool:
        check_bad_value(session, Session, self, "session")
        if self.get_session(session.id):
            return False
        
        session.directory_level = len(self.directory_stack)
        try: session.last_directory = self.directory_stack[-1]
        except: pass
        
        self.__sessions[session.id] = session
        return True
        
    def get_session(self, id: str, expected_class: Type[SessionType] = Session
            ) -> SessionType | None:
        return self.__sessions.get(id) # type: ignore
    
    def update_sessions(self):
        new_dir_level = len(self.directory_stack)
        try: last_directory = self.directory_stack[-1]
        except: last_directory = None
        delete = []
        for session in self.sessions:
            if not session.delete_if_level_decreased:
                continue
            if not session.directory_level > new_dir_level:
                continue
            delete.append(session)
            
        for session in self.sessions:
            if not session.delete_if_last_dir_changed:
                continue
            if session.last_directory == last_directory:
                continue
            delete.append(session)
        
        for session in delete:
            self.delete_session(session)
    
    def delete_session(self, session: Session):
        check_bad_value(session, Session, self, "session")
        del self.__sessions[session.id]
    
    def __repr__(self):
        return f"{type(self).__name__}({self.user_id!r})"

class UserDataManager:
    def __init__(self):
        self.__users_data: dict[int, UserData] = {}
        self.users_data = self.__users_data
    
    def get(self, user_id: int) -> UserData:
        user_data = self.__users_data.get(user_id)
        if user_data is None:
            user_data = UserData(user_id)
            self.set(user_id, user_data)
        return user_data
    
    def reset(self, user_id: int) -> None:
        self.set(user_id, UserData(user_id))
    
    def set(self, user_id: int, user_data: UserData):
        self.__users_data[user_id] = user_data
