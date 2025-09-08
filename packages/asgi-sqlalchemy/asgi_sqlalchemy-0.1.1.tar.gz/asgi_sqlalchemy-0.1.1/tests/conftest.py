"""Pytest common testing utilities."""

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
import uvloop
from testcontainers.postgres import PostgresContainer
from uvloop import EventLoopPolicy

from asgi_sqlalchemy.context import DatabaseContext


@pytest_asyncio.fixture(
    params=["sqlite", "postgres:17", "postgres:16", "postgres:15", "postgres:14"]
)
async def database(request: pytest.FixtureRequest) -> AsyncGenerator[DatabaseContext]:
    """Provide a mock sqlite database."""
    if request.param.startswith("postgres:"):
        is_postgres = True
        container = PostgresContainer(request.param)
        container.start()
        # seems to be necessary to wait for the container to be ready
        await asyncio.sleep(2)
        db_url = container.get_connection_url(driver="asyncpg")
    elif request.param == "sqlite":
        is_postgres = False
        db_url = "sqlite+aiosqlite:///:memory:"
    else:
        msg = f"Invalid database type: {request.param}"
        raise ValueError(msg)

    async with DatabaseContext(
        db_url,
        engine_kwargs={"pool_pre_ping": True},
        session_kwargs={"autoflush": False, "expire_on_commit": False},
    ) as db:
        yield db

    if is_postgres:
        container.stop()


@pytest.fixture(scope="session")
def event_loop_policy() -> EventLoopPolicy:
    """Set pytest event loop to uvloop."""
    return uvloop.EventLoopPolicy()
