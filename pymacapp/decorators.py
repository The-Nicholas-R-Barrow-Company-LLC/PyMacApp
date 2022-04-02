from .logger import logger
from functools import wraps

def deprecated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.critical(f"{f.__name__} is deprecated and will be removed in the future")
        return f(*args, **kwargs)
    return decorated