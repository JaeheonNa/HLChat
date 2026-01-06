from unittest.mock import Mock
from application.port.input.userUsecase import FindUserUsecase, SaveTempUserUsecase
from application.service.userService import FindUserService, SaveTempUserService
from domain.response import UserListSchema, UserSchema
from main import app

def test_find_all_users(test_client, mocker):
    from domain.orm import User
    user = User(user_id="P14514", user_name="나재헌", active=True)
    expected_response = UserListSchema(users=[user])

    # 모킹
    mock_usecase = Mock(spec=FindUserUsecase)
    mock_usecase.findAllUsers.return_value = expected_response
    # 의존성 교체
    def override_find_all_users_usecase():
        return mock_usecase
    app.dependency_overrides[FindUserService] = override_find_all_users_usecase

    # 테스트 실행
    response = test_client.get("/user")
    assert response.status_code == 200
    assert response.json() == {"users":[
        {
            "user_id":"P14514",
            "user_name":"나재헌",
            "active":True
         }
    ]}

def test_save_temp_user(test_client, mocker):
    expected_return = UserSchema(user_id="P14514", active=False)

    # 모킹
    mock_usecase = Mock(spec=SaveTempUserUsecase)
    mock_usecase.saveTempUser.return_value = expected_return
    # 의존성 교체
    def override_add_user_usecase():
        return mock_usecase
    app.dependency_overrides[SaveTempUserService] = override_add_user_usecase

    requestBody = {"user_id":"P14514"}
    response = test_client.post("/user/temp", json=requestBody)
    assert response.status_code == 201
    assert response.json() == {"user_id":"P14514", "active": False, "user_name":None}