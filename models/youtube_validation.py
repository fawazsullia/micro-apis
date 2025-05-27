from pydantic import BaseModel

class Extract_Youtube_Transacription(BaseModel):
    link: str

class Extract_Content_From_Transcript(BaseModel):
    content: str