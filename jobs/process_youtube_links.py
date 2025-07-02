from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
from schemas import ContentJob, ContentModel, BlogModel
import asyncio
from enums import JobStatus, JobContext
import logging
from datetime import datetime
from services import YoutubeService


logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()

async def process_content(content_job: ContentJob):
    content_id = content_job.content_id
    if not content_id:
        logging.error("Content ID is missing in the content job.")
        return
    content = await ContentModel.get(content_id)
    if content_job.context == JobContext.BLOG:
        await process_blog_content(content_job, content)

async def process_blog_content(content_job: ContentJob, content: ContentModel):
    content_id = str(content.id)
    youtube_service = YoutubeService()
    blog_post = await youtube_service.extract_content_from_transcript(content.raw_text)
    if not blog_post:
        logging.error(f"Failed to extract content from transcript for content ID {content_id}.")
        return
    blog_post_data = BlogModel(
        contentId=content_id,
        data=blog_post,
        is_active=True,
        job_id=str(content_job.id),
    )
    await blog_post_data.insert()
    content.blogs.append(blog_post_data)
    content.updated_at = datetime.utcnow()
    await content.save()
    return

async def process_next_job():
    content_job = None
    try:
        content_job = await ContentJob.find_one({
            "completed": False,
            "status": JobStatus.PENDING
        })

        if not content_job:
            logging.info("No pending job found.")
            return

        logging.info(f"Processing job {content_job.id}")
        content_job.status = JobStatus.IN_PROGRESS
        content_job.updated_at = datetime.utcnow()
        await content_job.save()

        # Simulate actual processing
        await process_content(content_job=content_job)

        content_job.status = JobStatus.COMPLETED
        content_job.completed = True
        content_job.updated_at = datetime.utcnow()
        content_job.metadata = {"processed_at": str(datetime.utcnow())}
        await content_job.save()

        logging.info(f"Job {content_job.id} completed.")
    except Exception as e:
        if content_job:
            content_job.status = JobStatus.FAILED
            content_job.error = str(e)
            content_job.updated_at = datetime.utcnow()
            await content_job.save()
        logging.error(f"Error processing job: {e}")


def start_yt_processing_scheduler():
    print("Starting scheduler...")
    scheduler.add_job(process_next_job, 'interval', seconds=60)
    scheduler.start()
