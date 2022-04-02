import logging

logger = logging.Logger(__name__)
formatter = logging.Formatter("%(asctime)s pymacapp >>> %(filename)s @ %(lineno)d in .%(funcName)s(...) [%(levelname)s]: %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)