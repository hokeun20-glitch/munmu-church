import os
import sys
import traceback

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CWD_DIR = os.getcwd()

for p in [ROOT_DIR, CWD_DIR]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app
    handler = app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    err_app = FastAPI()
    err_trace = traceback.format_exc()
    
    @err_app.get("/{full_path:path}")
    def error_diagnostics(full_path: str):
        return HTMLResponse(
            content=f"""
            <div style="font-family: sans-serif; padding: 30px; max-width: 800px; margin: auto;">
              <h2 style="color: #c0392b;">문무대교회 Vercel 서버리스 실행 진단</h2>
              <p>파이썬 모듈 로딩 중 예외가 발생했습니다:</p>
              <pre style="background: #2d3436; color: #dfe6e9; padding: 20px; border-radius: 8px; overflow-x: auto;">{err_trace}</pre>
            </div>
            """,
            status_code=200
        )
    
    handler = err_app
    app = err_app
