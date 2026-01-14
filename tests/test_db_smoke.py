import os

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_connectivity_select_one():
    url = os.getenv("SUPABASE_DATABASE_URL")
    if not url:
        pytest.fail("SUPABASE_DATABASE_URL is not set in the environment for tests")

    engine = create_async_engine(url, echo=False)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar_one()
            assert value == 1
    finally:
        await engine.dispose()
