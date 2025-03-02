from fastapi import APIRouter

from models import EmailValidationRequest, EmailValidationResponse
from services import EmailValidation

router = APIRouter()

@router.post("/email")
async def validate_email(body: EmailValidationRequest) -> EmailValidationResponse:
    email_validator = EmailValidation(body.email)
    dict_validated = email_validator.to_dict()
    return dict_validated