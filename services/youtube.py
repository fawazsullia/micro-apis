from openai import OpenAI
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from .llm_service import Llm_Service
from prompts import get_blog_outline_prompt, get_blog_post_prompt, get_summary_prompt
from utils import json_to_clean_markdown
import json
from models import YTExtractionRequest
from schemas import ContentJob, ContentModel, UserModel
from datetime import datetime
from enums import JobStatus, JobContext
import logging
from .yt_transcript_fetch import YouTubeTranscriptExtractor
logging.basicConfig(level=logging.INFO)

client = OpenAI()
class YoutubeService:
    def __init__(self):
        pass

    async def extract_transcript(self, link: str):
        logging.info(f"Extracting transcript for link: {link}")
        # video_id = self.extract_video_id(link)
        yt_trnscript_extractor = YouTubeTranscriptExtractor()
        transcript = yt_trnscript_extractor.get_transcript(link)
        return transcript
    
    def extract_video_id(self, link: str) -> None:
        parsed_url = urlparse(link)

        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.hostname in ['youtu.be']:
            return parsed_url.path.lstrip('/')
        return None
    
    async def extract_content_from_transcript(self, content: str):
        content = content.replace('\n', ' ')
        content = re.sub(r'\s+', ' ', content).strip()
        llm_service = Llm_Service("gpt-4o")
        token_count = await llm_service.calculate_total_tokens(content)
        content_chunks = []
        if token_count > 10000:
            content_chunks = llm_service.split_text_into_token_chunks(content, model="gpt-4o", max_tokens=10000, overlap=1000)
            content = " ".join(content_chunks)
        else:
            content_chunks = [content]
        
        summaries = await self.get_summary_from_content_chunks(content_chunks, llm_service)
        content = " ".join(summaries)
        content = content.replace('\n', ' ')
        content = re.sub(r'\s+', ' ', content).strip()

        blog_outline = await llm_service.extract_data_from_llm(get_blog_outline_prompt(content))
        blog_post_json_string = await llm_service.extract_data_from_llm(get_blog_post_prompt(blog_outline))
        blog_post = json.loads(blog_post_json_string)
        return blog_post
    
    async def get_summary_from_content_chunks(self, content_chunks: list, llm_service: Llm_Service = None):
        if llm_service is None:
            # If no LLM service is provided, create a new instance
            # This allows for flexibility in using different LLM services if needed
            llm_service = Llm_Service("gpt-4o")
        summaries = []
        for chunk in content_chunks:
            summary = await llm_service.extract_data_from_llm(get_summary_prompt(chunk))
            summaries.append(summary)
        return summaries
    
    async def handle_yt_extraction_request(self, request: YTExtractionRequest, current_user: UserModel):
        """
        Handles the YouTube extraction request by extracting the transcript and content.
        """
        
        existing_content = await ContentModel.find_one(ContentModel.link == request.link)
        if existing_content:
            existing_content.updated_at = datetime.utcnow()
            await existing_content.save()
            return { "message": "Content already exists." }
        
        extract_transcript = await self.extract_transcript(request.link)
        content = ContentModel(
            userId=str(current_user.id),
            link=request.link,
            is_active=True,
            title=request.title,
            raw_text=extract_transcript[0]
        )
        content = await content.insert()

        content_jobs = []

        if request.blog == True:
            logging.info("Creating content job for blog extraction.")
            content_jobs.append(
                ContentJob (
                    content_id=str(content.id),
                    status=JobStatus.PENDING,
                    user_id=str(current_user.id),
                    metadata={"count": 1},
                    context=JobContext.BLOG
                )
            )
        if request.linked_in and request.linked_in.include:
            content_jobs.append(
                ContentJob (
                    content_id=str(content.id),
                    status=JobStatus.PENDING,
                    user_id=str(current_user.id),
                    metadata={"count": request.linked_in.count},
                    context=JobContext.LINKED_IN_POST
                )
            )

        if request.twitter and request.twitter.include:
            content_jobs.append(
                ContentJob (
                    content_id=str(content.id),
                    status=JobStatus.PENDING,
                    user_id=str(current_user.id),
                    metadata={"count": request.twitter.count},
                    context=JobContext.TWITTER_POST
                )
            )
        if request.facebook and request.facebook.include:
            content_jobs.append(
                ContentJob (
                    content_id=str(content.id),
                    status=JobStatus.PENDING,
                    user_id=str(current_user.id),
                    metadata={"count": request.facebook.count},
                    context=JobContext.FACEBOOK_POST
                )
            )
        if request.reddit and request.reddit.include:
            content_jobs.append(
                ContentJob (
                    content_id=str(content.id),
                    status=JobStatus.PENDING,
                    user_id=str(current_user.id),
                    metadata={"count": request.reddit.count},
                    context=JobContext.REDDIT_POST
                )
            )

        if not content_jobs:
            logging.info("No content jobs to create, returning early.")
            return { "message": "No content jobs to create." }
        
        # Insert all content jobs in bulk
        for job in content_jobs:
            await job.insert()

        return { "message": "Content created and extraction scheduled." }
    
