"""
Environment variable loader for the FastAPI project.
Loads .env and .env.local files in the correct order.
"""

from dotenv import load_dotenv


def load_environment() -> None:
    # Load .env first (static/build-time)
    load_dotenv(dotenv_path=".env", override=False)
    # Load .env.local next (secrets/env-specific, overrides .env)
    load_dotenv(dotenv_path=".env.local", override=True)
