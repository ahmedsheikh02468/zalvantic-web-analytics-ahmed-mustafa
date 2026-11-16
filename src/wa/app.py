from contextlib import asynccontextmanager
from fastapi import FastAPI
from wa.db import create_db_and_tables
from wa.routes.events import router as events_router
from wa.routes.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Zalvantic Web Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(events_router)
app.include_router(metrics_router)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Zalvantic Web Analytics API is running successfully!",
    }
