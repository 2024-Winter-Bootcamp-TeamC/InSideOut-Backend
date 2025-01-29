import io
import os
from fastapi import UploadFile, File, Form
from utils import vision 
from typing import List, Optional
from sqlalchemy.orm import Session
import redis, json
from crud.ai import seven_ai_one_response
import redis.asyncio as redis_asyncio

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_client = redis_asyncio.Redis(host=redis_host, port=redis_port, decode_responses=True)

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

user_counters = {}

async def file(db: Session, user_id: int, category: str, files: Optional[List[UploadFile]] = File(None), content: str = Form(...)):
    file_details = []
    global user_counters

    if user_id not in user_counters:
        user_counters[user_id] = 1  

    if files is None:
        files = []
    
    image = "No file uploaded"

    if files:  # 파일이 제공된 경우만 처리
        for file in files:
            n = user_counters[user_id]
            filename = f"{user_id}_{n}.jpeg"
            user_counters[user_id] += 1  

            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

        image = await vision.process_user_images(user_id)

    redis_key = f"user_{user_id}"
    redis_data = {"category": category, "content": content, "image": image}

    
    # 7가지 감정 한줄평
    prompts = json.dumps(redis_data, ensure_ascii=False)
    response = await seven_ai_one_response(prompts)
    
    await redis_save(user_id, redis_key, redis_data, category, content, response)

    return {"message": "success"}

async def redis_save(user_id: int,redis_key: str, redis_data:dict, category:str, content:str, response:str):
    await redis_client.set(redis_key, json.dumps(redis_data, ensure_ascii=False).encode('utf-8'))
    await redis_client.set(f"category_{user_id}", json.dumps(f"{category}", ensure_ascii=False).encode('utf-8'))
    await redis_client.set(f"content_{user_id}", json.dumps(f"{content}", ensure_ascii=False).encode('utf-8'))
    await redis_client.set(f"emotions_{user_id}", json.dumps(f"{response}", ensure_ascii=False).encode('utf-8'))

