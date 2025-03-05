from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from services import DocumentExtractor, ImageComparison
import json

router = APIRouter()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/summarize")
async def summarize_document(file: UploadFile = File(...)):
    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    extractor = DocumentExtractor()
    summary = await extractor.summarize(str(file_path))
    return { summary: summary}

@router.post("/extract_text")
async def extract_text(file: UploadFile = File(...)):
    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    extractor = DocumentExtractor()
    try:
        extracted_text = await extractor.extract(str(file_path))
        print("Extracted Text:\n", extracted_text)
        if not extracted_text or extracted_text.strip() == "":
            raise HTTPException(status_code=400, detail="Empty JSON response from extractor")
        extraction_result = json.loads(extracted_text)
        print("Extraction Result:\n", extraction_result)
        return JSONResponse(content=extraction_result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format returned from extractor") 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}") 
    
@router.post("/image_comparison")
async def compare_images(image: UploadFile = File(...), face_image: UploadFile = File(...)):
    file1_path = Path(UPLOAD_DIR) / image.filename
    file2_path = Path(UPLOAD_DIR) / face_image.filename
    with open(file1_path, "wb") as buffer:
        buffer.write(await image.read())
    with open(file2_path, "wb") as buffer:
        buffer.write(await face_image.read())
    comparer = ImageComparison()
    similarity = await comparer.compare_faces(str(file1_path), str(file2_path))
    return similarity
