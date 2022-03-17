from .setuptools import BuildConfig

class App:
    def __init__(self, name:str, identifier:str=None) -> None:
        self.name = name
        self.identifier = identifier
    
    def build(self, config:BuildConfig):
        self.config = config
        
        return self