import logging

logger = logging.Logger(__name__)
formatter = logging.Formatter("pymacapp >>> (%(asctime)s) %(filename)s @ %(lineno)d [%(levelname)s]: %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)