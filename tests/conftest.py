import pathlib

from dotenv import load_dotenv


# Load environment variables from the API .env to make DB/config available in tests.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env"

# Only load if present to avoid errors in clean setups.
if API_ENV_PATH.exists():
    load_dotenv(API_ENV_PATH)
