from pathlib import Path
import os

class FileExistsException(Exception):
    pass

class ProjectGenerator:
    def __init__(self, force: bool):
        self.force: bool = force
    
    def mkpackage(self, path: Path):
        try: os.mkdir(path) 
        except: ...
        
        init_path = path / "__init__.py"
        
        self.mkmodule(init_path, "")

    def mkmodule(self, path: Path | str, text: str):
        if not self.force and os.path.exists(path):
            raise FileExistsException(f"Файл существует: {path!s}")
        
        with open(path, mode="w", encoding="utf-8") as fh:
            fh.write(text)