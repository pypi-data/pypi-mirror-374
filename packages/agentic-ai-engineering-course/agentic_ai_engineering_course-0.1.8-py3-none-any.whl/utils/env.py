import os
import warnings
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv


def load(dotenv_path: Path | None = None, required_env_vars: list[str] | None = None) -> None:
    if dotenv_path is None:
        dotenv_path = Path().absolute().parent.parent / ".env"
    print(f"Trying to load environment variables from `{dotenv_path}`")

    if not dotenv_path.exists():
        warnings.warn(f"Environment file `{dotenv_path}` not found.")

    load_dotenv(dotenv_path=dotenv_path)

    if required_env_vars is not None:
        for env_var in required_env_vars:
            if env_var not in os.environ:
                manually_set_envvar(env_var)

    print("Environment variables loaded successfully.")


def manually_set_envvar(var: str) -> None:
    if not os.environ.get(var):
        os.environ[var] = getpass(f"Could not load `{var}` from environment file. Please enter it manually: ")
