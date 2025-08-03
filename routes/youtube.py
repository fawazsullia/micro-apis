from fastapi import APIRouter, Depends
from services.youtube import YoutubeService
from models.youtube_validation import Extract_Youtube_Transacription, Extract_Content_From_Transcript
from models import YTExtractionRequest
from middlewares import get_current_user

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


@router.post("/extract-twitter-posts")
async def extract_twitter_posts(body: Extract_Content_From_Transcript):
    count = 4
    youtube_service = YoutubeService()
    twitter_posts = await youtube_service.extract_twitter_posts(body.content, count)
    return twitter_posts


@router.post("/extraction-request")
async def extraction_request(body: YTExtractionRequest, current_user=Depends(get_current_user)):
    youtube_service = YoutubeService()
    content = await youtube_service.handle_yt_extraction_request(body, current_user)
    return content

@router.post("/extract-comments")
async def extract_comments(
    body: YTExtractionRequest
):
    youtube_service = YoutubeService()
    comments = await youtube_service.get_all_comments("pwAmNPaupVE")
    return comments