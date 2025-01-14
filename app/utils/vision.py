import os
import json
import base64
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

router = APIRouter()

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 환경 변수에서 API 키 읽기
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY")
if not GOOGLE_VISION_API_KEY:
    raise ValueError("환경 변수 'GOOGLE_VISION_API_KEY'가 설정되지 않았습니다.")

VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"


@router.get("/file_path")
async def process_user_images(user_id: int):
    user_files = [
        f for f in os.listdir(UPLOAD_DIR)
        if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and f.startswith(f"{user_id}_")
    ]

    if not user_files:
        raise HTTPException(
            status_code=404,
            detail=f"사용자 ID {user_id}에 해당하는 이미지 파일이 없습니다."
        )

    text_results = []

    for user_file in user_files:
        file_path = os.path.join(UPLOAD_DIR, user_file)
        try:
            with open(file_path, "rb") as image_file:
                content = image_file.read()

            # Base64로 인코딩
            encoded_image = base64.b64encode(content).decode("utf-8")

            # Vision API 요청 본문
            request_body = {
                "requests": [
                    {
                        "image": {
                            "content": encoded_image
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 1
                            }
                        ]
                    }
                ]
            }

            # Vision API 호출
            response = requests.post(
                VISION_API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(request_body)
            )

            # 응답 처리
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Vision API 오류: {response.text}"
                )

            response_data = response.json()
            annotations = response_data.get("responses", [{}])[0].get("textAnnotations", [])

            if annotations:
                text_results.append({
                    "filename": user_file,
                    "text": annotations[0]["description"].strip()
                })
            else:
                text_results.append({
                    "filename": user_file,
                    "text": "텍스트 감지 결과 없음"
                })

        except Exception as e:
            text_results.append({
                "filename": user_file,
                "error": f"파일 처리 중 오류 발생: {str(e)}"
            })

    return {
        "status": "success",
        "user_id": user_id,
        "results": text_results
    }
