from PySide6.QtCore import QEvent, QUrl
from PySide6.QtWidgets import QApplication
from ..logger import logger


class CustomURIApplication(QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_uri_do = None
        self.last_uri = None

    def on_uri_call(self, func):
        """
        Run func when an uri is sent to the application; access the uri @ CustomURIApplication.last_uri
        :param func: the function to run (WITHOUT "()" AT THE END); use lambda for parameters
        :return: None
        """
        self.on_uri_do = func

    def event(self, e):
        """Handle macOS FileOpen events or pass to super."""
        if e.type() == QEvent.FileOpen:
            url: QUrl = e.url()
            self.last_uri: QUrl = url
            if url.isValid():
                logger.info(f"application received valid uri: {url}")
                logger.debug(f"executing callback function")
                self.on_uri_do()
            else:
                logger.warning(f"application received invalid uri: {url.errorString()}")
        else:
            return super().event(e)
        return True
