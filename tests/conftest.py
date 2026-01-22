# conftest.py
import os
import pathlib
import pytest
from dotenv import load_dotenv

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
API_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env"
API_TEST_ENV_PATH = PROJECT_ROOT / "apps" / "api" / ".env.test"


def _read_supabase_url(path: pathlib.Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() != "SUPABASE_DATABASE_URL":
                continue
            candidate = value.strip().strip('"').strip("'")
            return candidate or None
    except OSError:
        return None
    return None


os.environ.setdefault("MERCURY_ENV", "test")
if "SUPABASE_DATABASE_URL" not in os.environ and API_TEST_ENV_PATH.exists():
    url = _read_supabase_url(API_TEST_ENV_PATH)
    if url:
        os.environ["SUPABASE_DATABASE_URL"] = url
    os.environ.setdefault("MERCURY_ENV_FILE", str(API_TEST_ENV_PATH))

if os.environ.get("MERCURY_ENV", "").lower() != "test" and API_ENV_PATH.exists():
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


@pytest.fixture(scope="session", autouse=True)
async def dispose_engine_at_session_end():
    yield
    import backend.db

    engine = getattr(backend.db, "_engine", None)
    if engine is not None:
        await engine.dispose()
    backend.db._engine = None
    backend.db._session_maker = None
