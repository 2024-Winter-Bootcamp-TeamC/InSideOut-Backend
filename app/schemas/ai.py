from pydantic import BaseModel
from typing import List

class UserInput(BaseModel):
    prompt: str
    emotions: List[str]

