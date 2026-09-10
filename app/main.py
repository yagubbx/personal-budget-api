from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import budget, transactions


def create_app(create_tables: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if create_tables:
            Base.metadata.create_all(bind=engine)
        yield

    application = FastAPI(
        title="Personal Budget API",
        description="Income and expense management REST API",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.include_router(transactions.router)
    application.include_router(budget.router)

    @application.get("/", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "message": "Personal Budget API is running"}

    return application


app = create_app()

