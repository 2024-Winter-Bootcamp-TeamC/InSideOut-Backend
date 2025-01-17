from pydantic import BaseModel
from typing import List, Optional,Dict

class Report(BaseModel):
    report_id: int
    category: str
    title: str

class ResponseStatus(BaseModel):
    status: str
    message: str

class CreateReport(BaseModel):
    report_id:int
    user_id:int
    situation_summary:str
    title:str
    emotion_summary:str
    category: str


class ReportsResponse(ResponseStatus):
    data: Optional[List[Report]]

class CreateResponse(ResponseStatus):
    report_id: int

class ReportResponse(ResponseStatus):
    title:str
    situation_summary:str
    emotion_summary: Dict[str, str]
    wording: Dict[str, str]
    emotion_percentage: Dict[str, float]

