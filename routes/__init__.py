from fastapi import APIRouter
from routes.validation import router as validation_router
from routes.document_extraction import router as document_extraction_router

api_router = APIRouter()

api_router.include_router(validation_router, prefix="/validate", tags=["validation"])
api_router.include_router(document_extraction_router, prefix="/document", tags=["document"])