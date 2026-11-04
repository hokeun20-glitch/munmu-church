import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가 (Vercel 서버리스 임포트 에러 방지)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

# Vercel ASGI Application 진입점
app = app
