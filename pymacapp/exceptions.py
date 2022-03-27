class BuildException(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(message, *args)