
1. 경로 이동 ---> cd ../../src        
2. 가상환경 생성 ---> python3.13 -m venv HLChat (버전은 반드시 3.11 이상이어야 함.)
3. 경로 이동 ---> cd ./HLChat
4. 가상환경 실행 ---> source bin/activate (bin 경로가 없다면, 가상환경 생성부터 다시 수행.)
5. 경로 이동 ---> cd ./src
6. 라이브러리 설치 ---> pip install -r requirements.txt
7. 어플리케이션 실행 ---> python server.py

pip freeze > requirements.txt (목록 생성)       
pip install -r requirements.txt (목록 설치)