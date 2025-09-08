"""Tests a mock FastAPI worker."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI, HTTPException, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from typing_extensions import TypedDict

from asgi_sqlalchemy.context import DatabaseContext
from asgi_sqlalchemy.fastapi import SessionDependency
from asgi_sqlalchemy.middleware import SessionMiddleware


@pytest_asyncio.fixture
async def fastapi_app(database: DatabaseContext) -> AsyncGenerator[FastAPI]:
    """FastAPI fixture with database lifespan."""

    class AppState(TypedDict):
        db: DatabaseContext

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[AppState]:  # noqa: ARG001
        yield {"db": database}

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(SessionMiddleware)  # type: ignore  # noqa: PGH003
    yield app
    del app.router


@pytest_asyncio.fixture
async def client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Create a test async client with lifespan support."""
    async with (
        LifespanManager(fastapi_app) as manager,
        AsyncClient(
            transport=ASGITransport(manager.app),
            base_url="http://test",
            follow_redirects=True,
        ) as client,
    ):
        yield client


async def test_successful_handler(fastapi_app: FastAPI, client: AsyncClient) -> None:
    """Tests that we can call a handler with no dependency and it works."""

    async def handler() -> dict[str, str]:
        return {"hello": "world!"}

    fastapi_app.add_api_route("/handle", handler, methods=["GET"])

    response = await client.get("/handle")
    assert response.status_code == 200
    assert response.json() == {"hello": "world!"}


async def test_database_unhandled_rollback(
    fastapi_app: FastAPI, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that an unhandled exception in our database rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text("""CREATE TABLE IF NOT EXISTS temp_test_table1 (
                value INTEGER
            )""")
        )
        await session.commit()

    error = "I am an unhandled exception!"

    async def trigger_error(session: SessionDependency) -> None:
        await session.execute(
            text("INSERT INTO temp_test_table1 (value) VALUES (2001)")
        )
        raise ValueError(error)

    fastapi_app.add_api_route("/error1", trigger_error, methods=["POST"])

    with pytest.raises(ValueError, match=error):
        await client.post("/error1")

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table1"))
        count = result.scalar()
        assert count == 0


async def test_database_doesnt_rollback(
    fastapi_app: FastAPI, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that a handled exception in our database rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text("""CREATE TABLE IF NOT EXISTS temp_test_table2 (
                value INTEGER
            )""")
        )
        await session.commit()

    error = "I am a handled exception!"

    async def trigger_error(session: SessionDependency) -> None:
        await session.execute(
            text("INSERT INTO temp_test_table2 (value) VALUES (2001)")
        )
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail=error)

    fastapi_app.add_api_route("/error2", trigger_error, methods=["POST"])

    response = await client.post("/error2")
    assert response.status_code == 303
    assert response.json() == {"detail": error}

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table2"))
        count = result.scalar()
        assert count == 1


async def test_database_manual_rollback(
    fastapi_app: FastAPI, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that a handled exception with a manual rollback rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text("""CREATE TABLE IF NOT EXISTS temp_test_table3 (
                value INTEGER
            )""")
        )
        await session.commit()

    error = "I am a handled exception!"

    async def trigger_error(session: SessionDependency) -> None:
        await session.execute(
            text("INSERT INTO temp_test_table3 (value) VALUES (2001)")
        )
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail=error)

    fastapi_app.add_api_route("/error3", trigger_error, methods=["POST"])

    response = await client.post("/error3")
    assert response.status_code == 303
    assert response.json() == {"detail": error}

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table3"))
        count = result.scalar()
        assert count == 0
