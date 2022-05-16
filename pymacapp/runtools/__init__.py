from PySide6.QtCore import QEvent, QUrl
from PySide6.QtWidgets import QApplication
from urirouter import URIRouter
from ..logger import logger


class CustomURIApplication(QApplication):

    def __init__(self, uri_scheme: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_uri = None
        self.router = URIRouter(uri_scheme)

    def event(self, e):
        """Handle macOS FileOpen events or pass to super."""
        if e.type() == QEvent.FileOpen:
            url: QUrl = e.url()
            self.last_uri: QUrl = url
            if url.isValid():
                logger.info(f"{self} received valid uri: {url}")
                self.router.handle(url.url())
            else:
                logger.warning(f"{self} received invalid uri: {url.errorString()} [IGNORING]")
        else:
            return super().event(e)
        return True
