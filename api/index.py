import os
import sys

# 프로젝트 루트 디렉토리를 sys.path에 확실하게 추가
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CWD_DIR = os.getcwd()

for p in [ROOT_DIR, CWD_DIR]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

# Vercel 런타임 호환 (app 및 handler 동시 지원)
handler = app
