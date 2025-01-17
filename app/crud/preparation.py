import io
import os
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException, status, File, Form
from utils import vision 
from typing import List
from sqlalchemy.orm import Session
import redis, json
from crud.ai import get_ai_responses
import redis.asyncio as redis_asyncio

redis_client = redis_asyncio.Redis(host="teamC_redis", port=6379, decode_responses=True)

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

user_counters = {}

# 이미지 검사
async def file(db: Session, user_id: int, category: str, files: List[UploadFile] = File(...), content: str = Form(...)):
    file_details = []
    global user_counters

    if user_id not in user_counters:
        user_counters[user_id] = 1  

    for file in files:
        n = user_counters[user_id]
        filename = f"{user_id}_{n}.jpeg"
        user_counters[user_id] += 1  

        # 파일 저장
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

    # 비전 API를 이용하여 이미지를 텍스트로 변환
    image = await vision.process_user_images(user_id)

    # 전체 내용 Redis에 저장
    redis_key = f"user_{user_id}"
    redis_data = {"category": category, "content": content, "image": image}

    # 7가지 감정 한줄평
    prompt = json.dumps(redis_data, ensure_ascii=False)
    response = await get_ai_responses(prompt)
   
    await redis_save(user_id, redis_key, redis_data, category, content, response)

    return {"message": "success"}

async def redis_save(user_id: int,redis_key: str, redis_data:dict, category:str, content:str, response:str):
    redis_client.set(redis_key, json.dumps(redis_data, ensure_ascii=False).encode('utf-8'))
    redis_client.set(f"category_{user_id}", json.dumps(f"category:{category}", ensure_ascii=False).encode('utf-8'))
    redis_client.set(f"content_{user_id}", json.dumps(f"content:{content}", ensure_ascii=False).encode('utf-8'))
    redis_client.set(f"emotions_{user_id}", json.dumps(f"emotions:{response}", ensure_ascii=False).encode('utf-8'))