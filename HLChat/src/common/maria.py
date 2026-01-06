

from config import mysql_url
from main import SessionFactory


def get_db():
    # SessionFactory.begin() -> Spring의 @Transactional
    with SessionFactory.begin() as session:
        yield session
        # 예외 없으면 자동 commit
        # 예외 발생 시 자동 rollback
