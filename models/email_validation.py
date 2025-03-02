from pydantic import BaseModel


class EmailValidationRequest(BaseModel):
    email: str

class EmailValidationResponse(BaseModel):
    email: str
    isSyntaxValid: bool
    isDomainValid: bool
    mxRecordsFound: bool
    isDisposable: bool
    isRoleBased: bool
    domain: str
    isFreeEmail: bool