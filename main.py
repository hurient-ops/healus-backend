from fastapi import FastAPI
from api.logs import router as logs_router
from core.database import engine
from models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healus Backend API", version="1.0.0")

app.include_router(logs_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Healus Backend API"}
