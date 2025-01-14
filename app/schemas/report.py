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
    