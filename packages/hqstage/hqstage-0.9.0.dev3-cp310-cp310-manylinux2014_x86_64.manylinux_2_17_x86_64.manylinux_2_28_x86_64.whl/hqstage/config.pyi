from _typeshed import Incomplete
from hqstage import models as models, system as system
from pathlib import Path
from platformdirs import PlatformDirsABC as PlatformDirsABC

SUPPORTED_PYTHON_VERSIONS: Incomplete

def get_venv_dir() -> Path:
    """Get the path to the virtual environment folder."""
def get_default_env_name() -> str:
    """Get the name of the default virtual environment."""
def get_config_file() -> Path:
    """Get the path to the config file.

    Returns:
        Path: The path to the config file.
    """
def get_configparser() -> models.HQStageConfig:
    """Get the configparser object for HQStage.

    Returns:
        configparser.ConfigParser: The configparser object.
    """
def write_config_parse_to_file(conf: models.HQStageConfig) -> None:
    """Write the configparser object to the config file.

    Args:
        conf (configparser.ConfigParser): The configparser object.
    """
def get_default_examples_dir() -> Path:
    """Get the default path to examples folder."""
def clean_config_dir() -> None:
    """Remove all files in the config directory."""
