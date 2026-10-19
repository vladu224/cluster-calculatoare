from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.database import Base, SessionLocal, engine
from app.seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Seed the database with an admin user
    with SessionLocal() as db:
        seed_admin(db)
    yield


app = FastAPI(title="Auth Service", root_path="/api/auth", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth" }