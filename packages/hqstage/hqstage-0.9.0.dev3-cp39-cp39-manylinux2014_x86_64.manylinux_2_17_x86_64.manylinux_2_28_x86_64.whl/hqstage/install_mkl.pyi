from hqstage import install as install, messages as messages, system as system
from hqstage.exceptions import HQStageException as HQStageException

def is_mkl_present() -> bool:
    """Check the presence of the MKL in a virtual environment.

    Checks if the MKL libraries are present in the virtual environment.

    Args:
        venv (Path | None): The path to the virtual environment.
    """
def install_mkl() -> None:
    """Install the MKL library into the specified virtual environment.

    Args:
        venv (Path | None): The path to the virtual environment.
    """
def create_mkl_symlinks() -> None:
    """Create symlinks for the MKL library in the specified virtual environment.

    WARNING: Windows support experimental only! This might NOT work as expected under Windows.

    Args:
        venv (Path | None): The path to the virtual environment.
    """
def ensure_mkl_in_environment() -> None:
    """Ensure the presence of the MKL library in the specified virtual environment.

    Checks if the MKL library is present and installs it if not.
    Then creates symlinks for the MKL library in the specified virtual environment.

    Args:
        venv (Path | None): The path to the virtual environment.
    """
