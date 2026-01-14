import pathlib
import pytest
from dotenv import load_dotenv
from backend.db import get_engine
engine = get_engine()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env"

if API_ENV_PATH.exists():
    load_dotenv(API_ENV_PATH)

@pytest.fixture(scope="function", autouse=True)
async def reset_db_engine():
    """Dispose engine after each test to prevent loop contamination."""
    yield
    await engine.dispose()

    
