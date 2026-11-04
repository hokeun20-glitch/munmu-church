import uvicorn
import webbrowser
import os
import sys
from app.database import init_db
from app.seed_data import seed

def main():
    print("=" * 60)
    print("  육군학생군사학교 문무대교회 웹 플랫폼 서버를 시작합니다.")
    print("=" * 60)
    
    # DB 및 시드 데이터 초기화
    init_db()
    seed()
    
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    print(f"\n[안내] 메인 웹사이트: {url}")
    print(f"[안내] 군종행정 관리자: {url}/admin  (ID: admin / PW: munmu1234!)")
    print(f"[안내] 3D 가상 목양실: {url}/virtual-space\n")

    # 브라우저 자동 실행 (선택적)
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # 서버 실행 (백그라운드 안정성을 위해 reload=False)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
