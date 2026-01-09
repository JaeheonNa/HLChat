from sqlalchemy import create_engine

from config import mysql_url
from sqlalchemy.orm import sessionmaker

class MySqlDB():
    def __init__(self):
        self.engine = None
        self.sessionFactory = None

    def connect(self):
        self.engine = create_engine(mysql_url, echo=True)  # echo=True: SQL을 로그로 찍는 옵션
        self.sessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def disconnect(self):
        self.engine.dispose()
        print("Disconnected to MySQL")

    def getSessionFactory(self):
        return self.sessionFactory

mysqlDB = MySqlDB()

def getMySqlDB():
    return mysqlDB

def getMySqlSession():
    # SessionFactory.begin() -> Spring의 @Transactional
    mysqlDB = getMySqlDB()
    if mysqlDB.getSessionFactory():
        with mysqlDB.getSessionFactory().begin() as session:
            yield session
            # 예외 없으면 자동 commit
            # 예외 발생 시 자동 rollback