import pytest
from database import clear_db


@pytest.fixture(scope="function", autouse=True)
def clear_tests():
    yield
    clear_db()

#유저 생성
def test_create_user(client):
    test_nickname = "test_nickname"
    test_password = "test_password"
    response = client.post(
        "/api/users/signup",
        json={"nickname":test_nickname, "password": test_password},
    )
    assert response.status_code ==200
    assert response.json()["nickname"] == test_nickname
    assert response.json()["password"] == test_password

#유저 조회
def test_find_user(client, user_id):

    response = client.get(
        f"/api/users/{user_id}"
        )

    expected_response = "test_nickname"
    assert response.text.strip('"') == expected_response

#유저를 찾지 못 할때
def test_find_user_not_found(client):
    invalid_user_id = 999

    response = client.get(
        f"/api/users/{invalid_user_id}"
        )

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "User not found"

#유저 로그인
def test_login_user(client, user_data):
    response = client.post(
        "/api/users/signup",
        json=user_data
    )
    assert response.status_code == 200

    login_response = client.post(
        "/api/users/login",
        json={"nickname": user_data["nickname"],"password":user_data["password"]},

    )

    assert login_response.status_code == 200
    login_data = login_response.json()

    assert login_data["status"] == "success"
    assert login_data["message"] == "Successfully logged in"
    assert "user_id" in login_data

#유저의 아이디가 존재하지 않을때
def test_login_user_not_found(client):
    noexist_user_data = {
        "nickname": "noexist_nickname",
        "password": "test_password",
    }

    response = client.post(
        "/api/users/login",
        json=noexist_user_data
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "The nickname doesn't exist"

#유저가 비밀번호를 다르게 입력했을때
def test_login_user_wrong_password(client):
    signup_response = client.post(
        "/api/users/signup",
        json={
            "nickname": "test_nickname",
            "password": "test_password",
        }
    )
    assert signup_response.status_code == 200

    wrong_password_user_data ={
        "nickname": "test_nickname",
        "password": "wrong_password",
    }

    response = client.post(
        "/api/users/login",
        json=wrong_password_user_data
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] =="The password is not correct"

#유저 삭제
def test_delete_user(client, user_data):
    signup_response = client.post(
        "/api/users/signup",
        json=user_data
    )
    assert signup_response.status_code == 200 

    user_id = signup_response.json()["id"]

    delete_response = client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == 200  

    delete_data = delete_response.json()
    assert delete_data["status"] == "success"
    assert delete_data["message"] == "User deleted successfully"

    #삭제가 이미 완료되었을때
    delete_again_response = client.delete(f"/api/users/{user_id}")
    assert delete_again_response.status_code == 400

    delete_again_data = delete_again_response.json()
    assert delete_again_data["detail"] == "User already deleted"

#삭제하려는 유저가 없을때
def test_delete_noexist_user(client):
    invalid_user_id = 999
    response = client.delete(f"/api/users/{invalid_user_id}")
    assert response.status_code == 404

    response_data = response.json()
    assert response_data["detail"] == "User not found"