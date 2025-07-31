from fastapi import APIRouter, Depends, Query
from beanie.operators import In
from schemas import ContentModel, ContentJob, BlogModel, SocialModal
from middlewares import get_current_user  # assumes you have an auth system
from models import PaginatedContentWithJobs, ContentWithJobs, ContentJobOut
from bson import ObjectId


router = APIRouter()

@router.get("/contents-with-jobs", response_model=PaginatedContentWithJobs)
async def get_contents_with_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.id)

    total = await ContentModel.find(ContentModel.userId == user_id).count()
    contents = await ContentModel.find(ContentModel.userId == user_id).skip(skip).limit(limit).to_list()

    if not contents:
        return {"total": 0, "items": []}

    content_ids = [str(content.id) for content in contents]

    jobs = await ContentJob.find(In(ContentJob.content_id, content_ids)).to_list()

    jobs_map = {}
    for job in jobs:
        jobs_map.setdefault(job.content_id, []).append(job)

    # 5. Prepare response
    result = []
    for content in contents:
        result.append(
            ContentWithJobs(
                id=str(content.id),
                userId=content.userId,
                link=content.link,
                title=content.title,
                created_at=content.created_at,
                updated_at=content.updated_at,
                jobs=[ContentJobOut(**job.dict(by_alias=True)) for job in jobs_map.get(str(content.id), [])]
            )
        )

    return {"total": total, "items": result}


@router.get("/content-with-jobs/{content_id}", response_model=ContentWithJobs)
async def get_content_with_jobs(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user.id)

    content = await ContentModel.get(content_id)
    if not content or content.userId != user_id:
        return {"error": "Content not found or access denied."}

    jobs = await ContentJob.find(ContentJob.content_id == content_id).to_list()

    return ContentWithJobs(
        id=str(content.id),
        userId=content.userId,
        link=content.link,
        title=content.title,
        created_at=content.created_at,
        updated_at=content.updated_at,
        blogs=content.blogs,
        raw_text=content.raw_text,
        tags=content.tags,
        is_active=content.is_active,
        socials=content.socials,
        jobs=[ContentJobOut(**job.dict(by_alias=True)) for job in jobs]
    )

@router.get("/blogs/{content_id}", response_model=list[BlogModel])
async def get_blogs(
    content_id: str,
    current_user: dict = Depends(get_current_user)
) -> list[BlogModel]:
    user_id = str(current_user.id)
    content = await ContentModel.get(content_id)
    if not content or content.userId != user_id:
        return {"error": "Content not found or access denied."}

    blogs = await BlogModel.find(
        BlogModel.contentId == content_id,
    ).to_list()
    return blogs if blogs else []

@router.get("/socials/{content_id}/{type}", response_model=list[SocialModal])
async def get_content_of_type(
    content_id: str,
    type: str,
    current_user: dict = Depends(get_current_user)
) -> list[SocialModal]:
    user_id = str(current_user.id)
    content = await ContentModel.get(content_id)
    if not content or content.userId != user_id:
        return {"error": "Content not found or access denied."}

    socials = await SocialModal.find(
        SocialModal.contentId == content_id,
        SocialModal.type == type
    ).to_list()
    return socials if socials else []