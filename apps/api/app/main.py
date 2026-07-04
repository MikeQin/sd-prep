from fastapi import FastAPI

from app.db import Base, SessionLocal, engine
from app.routes import router
from app.seed import seed_database

app = FastAPI(title="Rilla Coaching Insights API")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
