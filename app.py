from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import api_router

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting up...")  # Add logs to track execution
    yield
    print("Shutting down...")

app = FastAPI(title="Micro Apis", lifespan=life_span, openapi_url="/open-api", redoc_url="/redoc")
app.include_router(api_router, prefix="/api/v1")

@app.get("/api/live", tags=["Root"])
async def live():
    return {"message": "Service is live"}
