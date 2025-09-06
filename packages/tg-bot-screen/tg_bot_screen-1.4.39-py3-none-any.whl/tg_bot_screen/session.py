from typing import Any

class Session:
    def __init__(self, id: str, delete_if_level_decreased = True, 
            delete_if_last_dir_changed = False):

        self.id = id
        
        self.directory_level: int = None
        self.last_directory: str = None
        
        self.delete_if_level_decreased = delete_if_level_decreased
        self.delete_if_last_dir_changed = delete_if_last_dir_changed
    
    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r})"

class InputSession(Session):
    def __init__(self, id: str, delete_if_level_decreased = True, 
            delete_if_last_dir_changed = False,add_new_messages = True, 
            may_pop_last_input = True):
        
        super().__init__(id, delete_if_level_decreased, delete_if_last_dir_changed)
        
        self.messages = []
        self.add_new_messages = add_new_messages
        self.may_pop_last_input = may_pop_last_input
    
    def append(self, message: Any):
        self.messages.append(message)