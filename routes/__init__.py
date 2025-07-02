from fastapi import APIRouter
from routes.validation import router as validation_router
from routes.document_extraction import router as document_extraction_router
from routes.youtube import router as youtube_router
from routes.auth import app as auth_router
from routes.content import router as content_router

api_router = APIRouter()

api_router.include_router(validation_router, prefix="/validate", tags=["validation"])
api_router.include_router(document_extraction_router, prefix="/document", tags=["document"])
api_router.include_router(youtube_router, prefix="/yt", tags=["youtube"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(content_router, prefix="/content", tags=["content"])