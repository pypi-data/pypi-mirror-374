from hqstage import config as config
from hqstage.exceptions import HQStageException as HQStageException

def get_relative_scripts_dir() -> str:
    '''Get the relative path to the scripts folder.

    On Windows this resultsin "Scripts" and on POSIX systems this results in "bin".

    Returns:
        str: The relative path to the scripts folder.
    '''
def get_activate_script() -> str:
    """Get the name of the shell dependent activate script for a venv.

    Returns:
        str: The name of the activate script.
    """
def runs_on_windows() -> bool:
    """Check if the current system runs on Windows.

    Returns:
        bool: True if the current system runs on Windows, False otherwise.
    """
def check_python_version_supported() -> None:
    """Check if the current Python version is supported.

    Raises:
        HQStageException: If the current Python version is not supported.
    """
def detect_virtualenv() -> str:
    """Find the virtual environment path for the current Python executable.

    Returns:
        str: The path to the virtual environment.
    """
