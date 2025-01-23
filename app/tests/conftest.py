import sys, os

sys.path.append("app/")
os.environ["TESTING"] = "True"

import pytest
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, engine
from fastapi.testclient import TestClient
from models import *
import io

# 테스트용 세션 및 DB 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

test_nickname = "test_nickname"
test_password = "test_password"

# FastAPI 의존성 오버라이드
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 테스트 클라이언트 생성
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def user_data():
    return {"id":1,"nickname": test_nickname,"password":test_password}

@pytest.fixture(scope="function")
def user_id(client,user_data):
    response = client.post(
        "/api/users/signup",
        json=user_data,
    )
    return response.json()["id"]
    

@pytest.fixture
def test_files():
    file_content = b"test image content"
    file_name = "test_image.jpeg"
    files = {
        "files": (file_name, io.BytesIO(file_content), "image/jpeg")
    }
    return files

@pytest.fixture
def test_user_data():
    return {
        "user_id": 1,
        "category": "test_category",
        "content": "test_content"
    }

