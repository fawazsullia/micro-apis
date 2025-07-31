from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
from schemas import ContentJob, ContentModel, BlogModel, SocialModal, SocialData, CommentModel, Comment
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
        content_job.status = JobStatus.COMPLETED
        content_job.completed = True
    if content_job.context == JobContext.TWITTER_POST:
        await process_twitter_posts(content_job, content)
        content_job.status = JobStatus.COMPLETED
        content_job.completed = True
    if content_job.context == JobContext.REDDIT_POST:
        await process_reddit_posts(content_job, content)
        content_job.status = JobStatus.COMPLETED
        content_job.completed = True
    if content_job.context == JobContext.COMMENT_SENTIMENT_ANALYSIS:
        await process_comment_sentiment_analysis(content_job, content)
        content_job.status = JobStatus.COMPLETED
        content_job.completed = True
    if content_job.context == JobContext.COMMENT_IDEA_GENERATION:
        await process_comment_idea_generation(content_job, content)
        content_job.status = JobStatus.COMPLETED
        content_job.completed = True

async def process_comment_sentiment_analysis(content_job: ContentJob, content: ContentModel):
    content_id = str(content.id)
    comments = await CommentModel.find_one(CommentModel.contentId == content_id, CommentModel.is_active == True)
    youtube_service = YoutubeService()
    if not comments:
        comments = await youtube_service.extract_comments(content.raw_text)
        comments = CommentModel(
            contentId=content_id,
            comments=[Comment(text=comment.text, name=comment.name) for comment in comments],
            is_active=True,
            job_id=str(content_job.id),
        )
        await comments.insert()
    return

async def process_comment_idea_generation(content_job: ContentJob, content: ContentModel):
    content_id = str(content.id)
    comments = await CommentModel.find_one(CommentModel.contentId == content_id, CommentModel.is_active == True)
    youtube_service = YoutubeService()
    if not comments:
        comments = await youtube_service.extract_comments(content.raw_text)
        comments = CommentModel(
            contentId=content_id,
            comments=[Comment(text=comment.text, name=comment.name) for comment in comments],
            is_active=True,
            job_id=str(content_job.id),
        )
        await comments.insert()
    # Here you would implement the logic to generate ideas based on the comments
    # For now, we will just log that this step was reached
    logging.info(f"Generated ideas for content ID {content_id} based on comments.")
    return

async def process_reddit_posts(content_job: ContentJob, content: ContentModel):
    content_id = str(content.id)
    youtube_service = YoutubeService()
    reddit_posts = await youtube_service.extract_reddit_posts(content.raw_text, content_job.metadata.get("count", 1))
    if not reddit_posts:
        logging.error(f"Failed to extract Reddit posts for content ID {content_id}.")
        return
    social_posts = []
    for post in reddit_posts.posts:
        post_data = SocialModal(
            contentId=content_id,
            data=SocialData(
                content=post.content,
                hashTags=post.hashtags,
                title=post.title,
                tone=post.tone
            ),
            is_active=True,
            job_id=str(content_job.id),
            type=JobContext.REDDIT_POST,
        )
        social_posts.append(post_data)
    await SocialModal.insert_many(social_posts)
    content.updated_at = datetime.utcnow()
    await content.save()
    return

async def process_twitter_posts(content_job: ContentJob, content: ContentModel):
    content_id = str(content.id)
    youtube_service = YoutubeService()
    twitter_posts = await youtube_service.extract_twitter_posts(content.raw_text, content_job.metadata.get("count", 1))
    if not twitter_posts:
        logging.error(f"Failed to extract Twitter posts for content ID {content_id}.")
        return
    social_posts = []
    for post in twitter_posts.posts:
        post_data = SocialModal(
            contentId=content_id,
            data=SocialData(
                content=post.content,
                hashTags=post.hashtags,
                title=post.title,
                tone=post.tone
            ),
            is_active=True,
            job_id=str(content_job.id),
            type=JobContext.TWITTER_POST,
        )
        social_posts.append(post_data)
    await SocialModal.insert_many(social_posts)
    content.updated_at = datetime.utcnow()
    await content.save()
    return

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
