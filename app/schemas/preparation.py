import io
from pydantic import BaseModel


#상황설명 텍스트
class description(BaseModel):
    description: str | None = None
