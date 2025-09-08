"""Async context manager for a database."""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing_extensions import Self, override

if TYPE_CHECKING:
    from types import TracebackType

__all__ = ("DatabaseContext",)


class DatabaseContext(AbstractAsyncContextManager["DatabaseContext"]):
    """Async context manager representing the lifespan of a database."""

    def __init__(
        self,
        url: str,
        engine_kwargs: dict[str, Any] | None = None,
        session_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the database with an engine and session maker."""
        self._engine = create_async_engine(
            url, **engine_kwargs if engine_kwargs is not None else {}
        )
        self._session_maker = async_sessionmaker(
            self._engine, **session_kwargs if session_kwargs is not None else {}
        )

    @override
    async def __aenter__(self) -> Self:
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.dispose()

    @property
    def engine(self) -> AsyncEngine:
        """Get a handle on the `AsyncEngine`."""
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get the internal `async_sessionmaker`."""
        return self._session_maker

    async def dispose(self) -> None:
        """Dispose of the engine."""
        await self._engine.dispose()
