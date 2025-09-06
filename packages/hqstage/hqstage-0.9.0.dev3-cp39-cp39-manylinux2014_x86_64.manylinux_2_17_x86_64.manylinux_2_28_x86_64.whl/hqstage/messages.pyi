from click import style as style

MODULE_COLOR: str
PACKAGE_COLOR: str
ENV_COLOR: str

def send_message(message: str) -> None:
    """Send a message to the user.

    Args:
        message (str): The message to send.
    """
