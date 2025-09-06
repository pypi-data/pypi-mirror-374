from hqstage import api as api, cache as cache, config as config, install as install, install_mkl as install_mkl, messages as messages
from hqstage.exceptions import HQStageException as HQStageException, HQStageUVException as HQStageUVException
from hqstage.models import HQStageEntitlement as HQStageEntitlement, HQStagePackage as HQStagePackage
from hqstage.uv import run_uv_in_python as run_uv_in_python
from pathlib import Path
from typing import Any

def show_all_entitled_modules() -> None:
    """Show all avaiable HQStage modules."""
def get_all_entitled_modules() -> list[HQStageEntitlement]:
    """Get all entitled HQStage modules for the user.

    Returns:
        list[str]: A list of HQStage modules for the given license.
    """
def get_user_entitlements() -> list[HQStageEntitlement]:
    """Gets all entitlements of the crrent user."""
def install_modules(names: list[str], yes: bool = False, requirements_files: list[Path] | None = None) -> None:
    '''Install HQStage modules and packages.

    Args:
        names (list[str]): Names of the modules and packages to install.
        yes (bool, optional): Confirm installation without prompting. Defaults to False.
        requirements_files (list[Path], optional): Paths to requirements files. Defaults to None.

    Example:
        hqstage install hqs_noise_app_py --yes
        hqstage install "HQS Qorrelator App" hqs-noise-app
        hqstage install "HQS Qorrelator App" hqs_noise_app_py
    '''
def install_names_to_modules_and_packages(names: list[str], entitled_modules: list[HQStageEntitlement]) -> tuple[list[str], list[str], list[str]]:
    """Find module codes and package names in the given list of entitlements.

    Args:
        names (list[str]): Names of modules / packages for install.
        entitled_modules (list[models.HQStageEntitlement]): List of entitlements to search in.

    Returns:
        tuple[list[str], list[str], list[str]]: List of module codes, package names, and error names.
            error_names (list[str]): List of names that were not recognized as modules or packages.
            module_codes (list[str]): List of module codes found in the names.
            package_names (list[str]): List of package names found in the names.
    """
def str_to_package(name: str, entitlements: list[HQStageEntitlement]) -> str | None:
    """Try to find a package name in the given list of entitlements.

    Args:
        name (str): The name to search for.
        entitlements (list[models.HQStageEntitlement]): List of entitlements to search in.

    Returns:
        str | None: The package name if found, or None otherwise.
    """
def str_to_module(name: str, entitlements: list[HQStageEntitlement]) -> str | None:
    """Try to find a module code in the given list of entitlements.

    Args:
        name (str): The name to search for.
        entitlements (list[models.HQStageEntitlement]): List of entitlements to search in.

    Returns:
        str | None: The module code if found, or None otherwise.
    """
def list_of_module_codes_to_list_of_package_names(module_codes: list[str], entitled_modules: list[HQStageEntitlement]) -> list[str]:
    """Convert a list of module codes to a list of package names.

    Args:
        module_codes (list[str]): List of module codes.
        entitled_modules (list[models.HQStageEntitlement]): List of entitled modules.

    Returns:
        list[str]: List of package names part of the module.
    """
def get_entitled_examples_packages() -> list[str]:
    """Get the list of entitled example packages.

    Returns:
        list[str]: List of entitled example packages.
    """
def get_examples_packages() -> list[str]:
    """Get the list of example packages.

    Returns:
        list[str]: List of example packages.
    """
def get_packages() -> list[dict[str, Any]]:
    """Get the list of available packages.

    Returns:
        list[str]: List of available packages.
    """
def download_examples(download_dir: Path | None = None, module_names: list[str] | None = None) -> tuple[list[str], list[str]]:
    """Download HQStage examples for your modules.

    You can provide a list of modules through the modules argument.
    The method will download available examples for those modules.
    If no modules are provided examples for all entitled modules will be downloaded.

    Args:
        download_dir (Path, optional): Path to the directory to download the examples to.
            Defaults to path defined in config.
        module_names (list[str], optional): Listof module names to download examples for.

    Returns:
        tuple[list[str], list[str]]: List of successfully downloaded and list of
            packages with errors.
    """
