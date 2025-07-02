from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import api_router
from schemas import init_db
from fastapi.middleware.cors import CORSMiddleware
from jobs import start_yt_processing_scheduler

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting up...")  # Add logs to track execution
    await init_db()
    start_yt_processing_scheduler()
    yield
    print("Shutting down...")

app = FastAPI(title="Micro Apis", lifespan=life_span, openapi_url="/open-api", redoc_url="/redoc")
origins = [
    "http://localhost:5173",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")

@app.get("/api/live", tags=["Root"])
async def live():
    return {"message": "Service is live"}
