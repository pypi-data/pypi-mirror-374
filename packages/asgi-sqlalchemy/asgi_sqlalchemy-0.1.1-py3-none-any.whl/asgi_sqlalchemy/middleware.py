"""ASGI middleware for session management."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from asgiref.typing import (
        ASGI3Application,
        ASGIReceiveCallable,
        ASGISendCallable,
        Scope,
    )

    from asgi_sqlalchemy.context import DatabaseContext

__all__ = ("SessionMiddleware",)


class SessionMiddleware:
    """Pure ASGI middleware that injects a database session into the `scope`."""

    def __init__(self, app: ASGI3Application) -> None:  # noqa: D107
        self.app = app

    async def __call__(  # noqa: D102
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        db = scope["state"].get("db")
        if scope["type"] != "http" or db is None:
            await self.app(scope, receive, send)
            return
        db = cast("DatabaseContext", db)
        async with db.session_maker() as session:
            scope["db_session"] = session  # type: ignore  # noqa: PGH003
            try:
                await self.app(scope, receive, send)
            except Exception:
                await session.rollback()
                raise
            await session.commit()
