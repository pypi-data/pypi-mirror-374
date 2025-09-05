from .common import *

def create_types(proj_gen: ProjectGenerator, cwd: Path): 
    proj_gen.mkpackage(cwd)
    