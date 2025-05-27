from openai import OpenAI
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from .llm_service import Llm_Service
from prompts import get_blog_outline_prompt, get_blog_post_prompt, get_summary_prompt

client = OpenAI()
class YoutubeService:
    def __init__(self):
        pass

    async def extract_transcript(self, link: str):
        video_id = self.extract_video_id(link)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transacription = ""
        for entry in transcript:
            transacription += entry['text']
        return transacription
    
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
        blog_post = await llm_service.extract_data_from_llm(get_blog_post_prompt(blog_outline))
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