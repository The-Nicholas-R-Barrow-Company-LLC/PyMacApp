import os, logging
from .defaultscripts import app

def main():
    # make logger
    logger = logging.Logger(__name__)
    logger.setLevel(logging.DEBUG)
    # make formatter
    formatter = logging.Formatter("(%(asctime)s) %(name)s @ %(lineno)d [%(levelname)s]: %(message)s")
    # make stream handler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.info("trying to create 'app' directory")
    try:
        path = os.path.join(os.getcwd(), "app")
        os.mkdir(path)
    except:
        logger.error(f"unable to create '{path}'")
        logger.error(f"unable to create template app.py file in '{path}'")
    else:
        logger.info("trying to create app.py in 'app' directory")
        try:
            path = os.path.join(os.getcwd(), "app", app.filename)
            with open(path, "w") as f:
                f.writelines(app.contents)
        except:
            logger.error(f"unable to create '{path}'")
    
    logger.info("trying to create 'dist' directory")
    try:
        path = os.path.join(os.getcwd(), "dist")
        os.mkdir(path)
    except:
        logger.error(f"unable to create '{path}'")
    
    logger.info("trying to create 'build' directory")
    try:
        path = os.path.join(os.getcwd(), "build")
        os.mkdir(path)
    except:
        logger.error(f"unable to create '{path}'")
        

if __name__ == "__main__":
    main()