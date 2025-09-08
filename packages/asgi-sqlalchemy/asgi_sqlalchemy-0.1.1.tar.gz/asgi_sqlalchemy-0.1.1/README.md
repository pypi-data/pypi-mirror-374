# asgi-sqlalchemy

ASGI Middleware that manages the lifespan of a database engine and a corresponding session.

## Usage:

### FastAPI:

```python
from contextlib import AsyncContextManager
from collections.abc import AsyncGenerator
from typing_extensions import TypedDict

from fastapi import FastAPI

from asgi_sqlalchemy import DatabaseContext, SessionMiddleware
from asgi_sqlalchemy.fastapi import SessionDependency

class AppState(TypedDict):
    db: DatabaseContext

async def lifespan() -> AsyncGenerator[AppState]:
    async with DatabaseContext(...) as db:
        yield {"db": db}

app = FastAPI()
app.add_middleware(SessionMiddleware)

@app.get("/db")
async def handler(session: SessionDependency) -> str:
    # do something with your async session!
```