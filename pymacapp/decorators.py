from .logger import logger
from functools import wraps

def deprecated(f, message:str=None):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.warn(message)
        return f(*args, **kwargs)
    return decorated