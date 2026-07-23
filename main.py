from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.logs import router as logs_router
from api.web import router as web_router
from core.database import engine
from models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healus Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router, prefix="/api")
app.include_router(web_router, prefix="/api/web")

@app.get("/")
def read_root():
    return {"message": "Welcome to Healus Backend API"}
