from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
import os
from typing import List
from database import get_db
from sqlalchemy.orm import Session
from crud import preparation

router = APIRouter()

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

user_counters = {}

@router.post("/", tags=["Preparation"])
async def upload_data(user_id: int, category: str, files: List[UploadFile] = File(...), content: str = Form(...), db: Session = Depends(get_db)):
    result = await preparation.file(db, user_id, category, files, content)
    return result