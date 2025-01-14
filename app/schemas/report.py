from pydantic import BaseModel
from typing import List, Optional

class Report(BaseModel):
    report_id: int
    category: str
    title: str

class ReportsResponse(BaseModel):
    status: str
    message: str
    data: Optional[List[Report]]

class ResponseError(BaseModel):
    status: str
    message: str

class CreateReport(Report):
    user_id:int
    situation_summary:str
    emotion_summary:str

class CreateResponse(BaseModel):
    status: str
    message: str
    report_id: int

