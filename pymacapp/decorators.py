from .logger import logger
from functools import wraps

def deprecated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.warn('.setup(...) is deprecated; .config(...) should be used instead')
        return f(*args, **kwargs)
    return decorated

@deprecated
def __hello_world__():
    print("hello world!")

if __name__ == "__main__":
    __hello_world__()