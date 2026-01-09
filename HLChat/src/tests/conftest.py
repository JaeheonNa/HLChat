import pytest
from fastapi.testclient import TestClient
from main import app


# 이렇게 해놓으면, pytest를 수행할 함수에 client 인자만 넣어주면 됨.
@pytest.fixture
def test_client():
    return TestClient(app=app)