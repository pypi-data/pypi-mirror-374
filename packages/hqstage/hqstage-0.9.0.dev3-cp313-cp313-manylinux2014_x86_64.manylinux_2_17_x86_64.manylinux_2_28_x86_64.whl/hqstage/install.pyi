from hqstage.api import create_get_request as create_get_request
from hqstage.exceptions import HQStageException as HQStageException
from pathlib import Path

def install_modules(names: list[str], upgrade: bool, dry_run: bool = False, requirements_files: list[Path] | None = None) -> None:
    """Install the HQStage modules spcified in names.

    This will install all the modules specified in names. The modules will be installed
    from HQS pypi server and will use the user defined in config to validate user
    entitlement to install the modules.

    If no user is defined in the config this method will fail. If you have not yet created
    a user for HQStage visit https://cloud.quantumsimulations.de and create a new user.

    Args:
        names (list[str]): Name of the modules to install.
        upgrade (bool): Whether to upgrade all installed packages while installing.
        dry_run (bool, optional): If True, the install command will not be executed. Defaults to False.
        requirements_files (list[Path], optional): Paths to requirements files. Defaults to None.
    """
def get_uv_pip_install_cmd(upgrade: bool, packages: list[str]) -> list[str]:
    """Generates pip install command for uv.

    If upgrade specified, it ensures that uv only updates the packages specified,
    not the dependent packages.


    Args:
        upgrade (bool): Updates the packages if it is already installed.
        packages (list[str]): Packages to install.

    Returns:
        list[str]: Commands line arguments for uv pip install command.
    """
