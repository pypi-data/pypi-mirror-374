"""FastAPI-specific dependency resolution utilities."""

from importlib.util import find_spec
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

if find_spec("fastapi") is not None:
    from fastapi import Depends, Request
else:  # pragma: no cover
    msg = "FastAPI not found, please install asgi-sqlalchemy[fastapi]"
    raise ImportError(msg)

__all__ = ("SessionDependency", "get_session")


async def get_session(request: Request) -> AsyncSession:
    """Get the `AsyncSession` put in the scope of the request via Middleware."""
    return request.scope.get("db_session")  # type: ignore  # noqa: PGH003


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
