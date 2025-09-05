import subprocess  # noqa: S404
import sys

from dsp_toolkit.env import load_environment
from dsp_toolkit.logging_config import logger


def test() -> None:
    """
    Run tests using pytest. Accepts additional arguments.
    """
    args = sys.argv[1:]  # get args after 'test'
    # S603: Validate args to avoid execution of untrusted input
    if any(arg.startswith("-") and not arg.replace("-", "").isalnum() for arg in args):
        logger.error("Unsafe argument detected.")
        sys.exit(1)

    sys.exit(subprocess.call([sys.executable, "-m", "pytest", *args]))  # noqa: S603


def lint_and_format() -> None:
    """
    Run Ruff to format code and fix lint issues (including import sorting),
    then run Flake8 for additional lint checks.
    Accepts additional arguments (e.g., directories or files).
    """
    args = sys.argv[1:]
    # S603: Validate args to avoid execution of untrusted input
    if any(arg.startswith("-") and not arg.replace("-", "").isalnum() for arg in args):
        logger.error("Unsafe argument detected.")
        sys.exit(1)

    # Ruff format and fix
    ruff_result = subprocess.call([sys.executable, "-m", "ruff", "format", *args])  # noqa: S603
    ruff_result |= subprocess.call([sys.executable, "-m", "ruff", "check", "--fix", *args])  # noqa: S603

    # Flake8 lint
    flake8_result = subprocess.call([sys.executable, "-m", "flake8", *args])  # noqa: S603
    sys.exit(ruff_result | flake8_result)


def release() -> None:
    """
    Run semantic-release to publish a new release. Accepts additional arguments.
    """
    args = sys.argv[1:]
    # S603: Validate args to avoid execution of untrusted input
    if any(arg.startswith("-") and not arg.replace("-", "").isalnum() for arg in args):
        logger.error("Unsafe argument detected.")
        sys.exit(1)
    sys.exit(subprocess.call([sys.executable, "-m", "semantic_release", *args]))  # noqa: S603


def main() -> None:
    """
    Main entry point for development server.
    Loads environment, finds free port, and starts FastAPI app with Uvicorn.
    """
    logger.info("Development mode activated")

    load_environment()

    logger.info("Loaded environment variables using load_environment() helper.")


if __name__ == "__main__":
    main()
