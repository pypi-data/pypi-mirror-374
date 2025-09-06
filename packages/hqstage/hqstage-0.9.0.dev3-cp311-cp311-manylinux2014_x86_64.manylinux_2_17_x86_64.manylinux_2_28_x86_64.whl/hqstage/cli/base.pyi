from hqstage import config as config, messages as messages, models as models, modules as modules
from hqstage.exceptions import HQStageException as HQStageException
from pathlib import Path

def show_modules() -> None:
    """Show your available HQStage modules and packages."""
def install_modules(names: list[str], yes: bool = False, all: bool = False, requirements: Path | None = None) -> None:
    '''Install HQStage modules and packages.

    Args:
        names (list[str]): Names of the modules and packages to install.
        yes (bool, optional): Confirm installation without prompting. Defaults to False.
        all (bool, optional): Install all available modules. Defaults to False.

    Example:
        hqstage install hqs_noise_app_py --yes
        hqstage install "HQS Qorrelator App" hqs-noise-app
        hqstage install "HQS Qorrelator App" hqs_noise_app_py
    '''
def init_hqstage(token_id: str | None, token: str | None, cloud_environment: models.CLOUD_ENVS | None) -> None:
    """Initialize HQStage."""
def init_user(token_id: str, token: str, cloud_environment: models.CLOUD_ENVS | None = None) -> models.HQStageProfile:
    '''Initialize a new user.

    If no user is defined in the config this method will fail. If you have not yet created
    a user for HQStage visit https://cloud.quantumsimulations.de and create a new user.

    Args:
        token_id (str): The token ID.
        token (str): The token.
        cloud_environment (Optional[str]): The cloud environment. Defaults to "cloud".

    Returns:
        HQStageProfile: The new profile.
    '''
def derive_cloud_environment(cloud_environment: models.CLOUD_ENVS | None) -> models.CLOUD_ENVS:
    """Decides how to derive the cloud environment.

    Explicitly passed in cloud environmnet
    via CLI argument takes precedence over environment variable. If no cloud environment CLI
     argument is found or environment variable, then fall back to default value of main cloud

    Args:
        cloud_environment (Optional[CLOUD_ENVS]): Cloud environment name

    Returns:
        str: cloud environment value required for the hqstage config file
    """
def download_examples(download_dir: Path | None = None, module_names: list[str] | None = None, list_available: bool = False) -> None:
    """Download HQStage examples for your modules.

    Provide module names with the command line argument -m or --modules.
    The command tries to find matching examples for incomplete names.
    If no modules name is provided, all available examples will be downloaded.

    Args:
        download_dir (Path, optional): The directory to download the examples to. Defaults to None.
        modules (list[str], optional): The modules to download examples for. Defaults to None.
        list_available (bool, optional): If True, list available examples. Defaults to False.

    Example:
        hqstage modules download-examples

    Example:
        hqstage modules download-examples -m hqs-qolossal -m raqet
    """
