from fastapi import FastAPI

app = FastAPI(title="Rilla Coaching Insights API")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
