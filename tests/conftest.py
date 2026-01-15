# conftest.py
import pathlib
import pytest
from dotenv import load_dotenv

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env"

if API_ENV_PATH.exists():
    load_dotenv(API_ENV_PATH)


@pytest.fixture(scope="function", autouse=True)
async def reset_db_engine():
    """Dispose engine after each test to prevent loop contamination."""
    yield
    
    from backend.db import get_engine
    engine = get_engine()
    await engine.dispose()
    
    # Reset globals so next test gets fresh engine
    import backend.db
    backend.db._engine = None
    backend.db._session_maker = None