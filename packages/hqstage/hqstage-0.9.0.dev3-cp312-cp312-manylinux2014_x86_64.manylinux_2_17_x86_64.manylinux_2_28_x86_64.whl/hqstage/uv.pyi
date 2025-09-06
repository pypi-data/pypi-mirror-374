import subprocess
from hqstage.exceptions import HQStageUVException as HQStageUVException
from pathlib import Path as Path

def pop_conda_prefix_from_env(env: dict[str, str]) -> dict[str, str]:
    """Remove the CONDA_PREFIX from the env dict.

    Warning:
        Changes the environment dictionary in place.

    Args:
        env (dict[str, str]): The environment dictionary.

    Returns:
        dict[str, str]: The environment dictionary without the CONDA_PREFIX key.
    """
def run_uv(*args) -> None:
    """Run uv with the given args replacing the current process.

    Warning:
        This will end the current (Python) process.

    Args:
        *args (list[str]): The arguments to pass to uv.
        venv (Path | None): The path to the virtual environment.
    """
def run_uv_in_python(*args, capture_output: bool = False) -> subprocess.CompletedProcess[bytes]:
    """Runs uv with the given arguments in a subprocess.

    Info:
        The current python process will continue to run.

    Args:
        *args (list[str]): The arguments to pass to uv.
        capture_output (bool): Whether to capture the output of the subprocess.

    Returns:
        subprocess.CompletedProcess[bytes]: The completed process.
    """
def run_uv_from_sysargs() -> None:
    """Runs uv with the commandline arguments in a subprocess.

    Warning:
        This will end the current (Python) process.
    """
def run_uv_in_pythonfrom_sysargs() -> None:
    """Runs uv with the commandline arguments in a subprocess.

    Info:
        The current python process will continue to run.
    """
