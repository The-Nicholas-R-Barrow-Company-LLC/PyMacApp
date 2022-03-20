import os
from .logger import logger

class Resource:
    def __init__(self, path:str) -> None:
        """creates a Resource object for a resource (file) based on 'path'

        :param path: path to the resource (file)
        :type path: str
        """
        if not os.path.isfile(path):
            logger.error(f"'{path}' is not a file (exists: {os.path.exists(path)})")
            raise RuntimeError(f"'{path}' is not a file (exists: {os.path.exists(path)})")
        else:
            self._name_ = os.path.basename(path)
            self._directory_ = os.path.dirname(path)
            self._relative_path_ = path
            self._absolute_path_ = os.path.abspath(path)
    
    # def add_to(self, app:App):
    #     app._resources_.append(self)
    #     return self
    
    def _get_pyinstaller_data(self) -> tuple:
        return (self._absolute_path_, self._directory_)
    
    def path(self) -> str:
        return self._relative_path_

    