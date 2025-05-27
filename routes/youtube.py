from fastapi import APIRouter
from services.youtube import YoutubeService
from models.youtube_validation import Extract_Youtube_Transacription, Extract_Content_From_Transcript

router = APIRouter()

@router.post("/extract")
async def extractyoutubeVideo(body: Extract_Youtube_Transacription):
    youtube_service = YoutubeService()
    transcription = await youtube_service.extract_transcript(body.link)
    return { "transcription": transcription }

@router.post("/extract-content")
async def extract_content_from_transcript(body: Extract_Content_From_Transcript):
    youtube_service = YoutubeService()
    content = await youtube_service.extract_content_from_transcript(body.content)
    return content
