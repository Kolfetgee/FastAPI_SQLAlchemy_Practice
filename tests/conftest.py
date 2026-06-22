from pathlib import Path
import asyncio
import os
import sys

import pytest
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["TESTING"] = "true"


from src.db.session import async_session, engine


async def reset_db() -> None:
    await engine.dispose()

    async with async_session() as session:
        await session.execute(
            text("TRUNCATE TABLE projects, users RESTART IDENTITY CASCADE")
        )
        await session.commit()

    await engine.dispose()


@pytest.fixture(autouse=True)
def clean_db() -> None:
    asyncio.run(reset_db())
    yield
    asyncio.run(reset_db())
