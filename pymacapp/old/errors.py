class ConfigAttributeError(Exception):
    """raise when the value attempting to be modified in a Config object cannot occur.
    """
    def __init__(self, msg) -> None:
        self.message = msg
        super().__init__(self.message)

class ConfigEmptyValueError(Exception):
    """raise when a value attempting to be modified in a Config cannot be None or an empty string.
    """
    def __init__(self, message:str="unable to assign None or empty-string value", *args: object) -> None:
        super().__init__(message, *args)