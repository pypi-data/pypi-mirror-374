from hqstage import config as config
from typing import Callable

def cache(ttl: int = 300) -> Callable:
    """Cache the result of a function.

    Args:
        ttl (int, optional): The time to live in seconds. Defaults to 300.
    """
