from click import ClickException

class HQStageException(ClickException):
    """HQStageException class."""
    def __init__(self, message: str) -> None:
        """HQStageException init."""

class HQStageUVException(HQStageException): ...
