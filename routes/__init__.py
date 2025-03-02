from fastapi import APIRouter
from routes.validation import router as validation_router

api_router = APIRouter()

api_router.include_router(validation_router, prefix="/validate", tags=["validation"])