import unittest
from unittest.mock import patch, MagicMock
from schemas.user import UserPostRequest,UserLoginRequest
from routers import user
from models import User
from datetime import datetime
from fastapi import HTTPException


class TestUserRouter(unittest.TestCase):

    #유저 생성
    def test_post_user(self):
        
        test_id = 1
        test_nickname = "test_nickname"
        test_password = "test_password"
        test_created_at = datetime.now()
        test_updated_at = datetime.now()

        new_user = UserPostRequest(nickname=test_nickname, password=test_password)

        
        with patch(
            "crud.user.create_user", 
            return_value=User(
                id=test_id,
                nickname=test_nickname,
                password=test_password,
                created_at=test_created_at,
                updated_at=test_updated_at,
            ),
        ):
            
            mock_db = MagicMock()  
            result = user.post_user(new_user=new_user, db=mock_db)

       
        assert result.id == test_id
        assert result.nickname == test_nickname
        assert result.password == test_password
        assert result.created_at == test_created_at
        assert result.updated_at == test_updated_at

    #유저 조회
    def test_get_user(self):
        test_id = 1
        test_nickname = "test_nickname"
        test_password = "test_password"
        test_created_at = datetime.now()
        test_updated_at = datetime.now()

        with patch(
            "crud.user.find_user",
            return_value=User(
                id=test_id,
                nickname=test_nickname,
                password=test_password,
                created_at=test_created_at,
                updated_at=test_updated_at,
             
            )
        ):
            mock_db = MagicMock()  # Mock 데이터베이스 세션 생성
            result = user.get_user(user_id=test_id, db=mock_db)
        assert result.id == test_id
        assert result.nickname == test_nickname
        assert result.password == test_password
        assert result.created_at == test_created_at
        assert result.updated_at == test_updated_at

    #유저 조회 불가
    def test_get_user_not_found(self):
        test_id = 1

        with patch(
            "crud.user.find_user",
            return_value={"status":"success","message":"Successfully logged in"},
        ):
        
            mock_db = MagicMock()
            result = user.get_user(user_id=test_id, db=mock_db)

        
        assert result["status"] == "success"
        assert result["message"] == "Successfully logged in"

    #유저 로그인
    def test_login_user(self):
        test_id = 1
        test_nickname = "test_nickname"
        test_password = "test_password"
        test_created_at = datetime.now()
        test_updated_at = datetime.now()

        login_data = UserLoginRequest(nickname=test_nickname, password=test_password)

        with patch(
            "crud.user.login_user",
            return_value=User(
            id = test_id,
            nickname = test_nickname,
            password = test_password,
            created_at = test_created_at,
            updated_at = test_updated_at,
            ),
        ):
            mock_db = MagicMock()
            result = user.login_user(login_data=login_data, db=mock_db)

            assert result.id == test_id
            assert result.nickname == test_nickname
            assert result.password == test_password
            assert result.created_at == test_created_at
            assert result.updated_at == test_updated_at

    #유저 삭제
    def test_delete_user(self):

        test_id=1
        
        with patch(
            "crud.user.delete_user",
            return_value={"status": "success", "message": "User deleted successfully"},
        ):  
            mock_db = MagicMock()
            result = user.delete_user(user_id=test_id,db=mock_db)

            assert result["status"] == "success"
            assert result["message"] == "User deleted successfully"
            








