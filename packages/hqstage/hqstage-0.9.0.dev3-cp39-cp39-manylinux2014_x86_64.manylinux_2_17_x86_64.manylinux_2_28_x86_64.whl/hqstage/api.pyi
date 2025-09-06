from _typeshed import Incomplete
from enum import Enum
from hqstage import cache as cache, config as config
from hqstage.exceptions import HQStageException as HQStageException
from typing import Any, TypedDict

TIMEOUT: int
VERIFY: bool
ACCEPT: str
PAGE_SIZE: int
SECONDS_TILL_NEW_CHECKOUT: Incomplete
CORE_API_VERSION: str

class AuthType(str, Enum):
    """Auth type for API requests."""
    BEARER = 'Bearer'

class RequestKWARGSDict(TypedDict):
    """Request kwargs for API requests."""
    headers: dict[str, Any]
    url: str
    verify: bool
    timeout: int

def create_get_request(path: str) -> RequestKWARGSDict:
    """Create a GET request to the HQS Licensing API.

    Returns:
        dict[str, Any]: The GET request kwargs for requests.get(**output).
    """
