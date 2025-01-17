from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.preparation import validate_image_type, validate_image_size, resize_image, save_image_to_filesystem
import os
from datetime import datetime
from typing import List

router = APIRouter()


UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


user_counters = {}

@router.post("/{user_id}", tags=["Preparation"])
async def upload_image(user_id: int, files: List[UploadFile] = File(...)):
    file_details = []

    global user_counters
    if user_id not in user_counters:
        user_counters[user_id] = 1  
    
   
    for file in files:
        n = user_counters[user_id]

        filename = f"{user_id}_{n}.jpeg"
        user_counters[user_id] += 1  

        await validate_image_type(file)
        await validate_image_size(file)

        
        image = resize_image(file)
        file_path = os.path.join(UPLOAD_DIR, filename)
        save_image_to_filesystem(image, file_path)

    return {
        "status": "success",
        "user_id": user_id,
        "uploaded_files": file_details
    }
