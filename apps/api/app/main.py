from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine, session_scope
from app.routes import router
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with session_scope() as db:
        seed_database(db)
    yield


app = FastAPI(title="Rilla Coaching Insights API", lifespan=lifespan)
app.include_router(router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
