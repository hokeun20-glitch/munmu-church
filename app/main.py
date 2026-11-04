import os
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import counseling, events, consolation, donation, church_info, admin
from app.bundle_cache import EMBEDDED_ASSETS

app = FastAPI(
    title="육군학생군사학교 문무대교회",
    description="ROTC·학사장교 후보생과 국군 장병의 영적 요람, 문무대교회 공식 웹 플랫폼",
    version="1.0.0"
)

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel rewrites(/api/index) 자동 경로 보정 미들웨어
class VercelPathFixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "")
            for prefix in ("/api/index.py", "/api/index"):
                if path.startswith(prefix):
                    new_path = path[len(prefix):]
                    if not new_path or not new_path.startswith("/"):
                        new_path = "/" + new_path
                    scope["path"] = new_path
                    break
        await self.app(scope, receive, send)

app.add_middleware(VercelPathFixMiddleware)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

try:
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
except Exception:
    pass

# 정적 파일 마운트 (로컬 호환)
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    pass

# 라우터 등록
app.include_router(counseling.router)
app.include_router(events.router)
app.include_router(consolation.router)
app.include_router(donation.router)
app.include_router(church_info.router)
app.include_router(admin.router)

# 십자가 파비콘 SVG
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#0f1d38"/>
  <rect x="13.5" y="4" width="5" height="24" rx="1.5" fill="#f5d77f"/>
  <rect x="6" y="10" width="20" height="5" rx="1.5" fill="#f5d77f"/>
</svg>"""

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

# Vercel 서버리스 정적 에셋 직접 서빙 폴백 (정적 폴더 누락 원천 차단)
@app.get("/static/{path:path}")
async def serve_static_fallback(path: str):
    local_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(local_path) and os.path.isfile(local_path):
        with open(local_path, "rb") as f:
            content = f.read()
    else:
        # 내장 번들에서 서빙
        key = f"static:static/{path}".replace("\\", "/")
        if key in EMBEDDED_ASSETS:
            content = EMBEDDED_ASSETS[key].encode("utf-8")
        else:
            return Response(content="File Not Found", status_code=404)

    media_type = "text/plain"
    if path.endswith(".css"): media_type = "text/css"
    elif path.endswith(".js"): media_type = "application/javascript"
    elif path.endswith((".jpg", ".jpeg")): media_type = "image/jpeg"
    elif path.endswith(".png"): media_type = "image/png"
    return Response(content=content, media_type=media_type)

def render_html_page(filename: str) -> HTMLResponse:
    """Vercel 서버리스에서도 100% 보장되는 템플릿 렌더링 엔진"""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except Exception:
            pass
            
    # 파일시스템 누락 시 내장 번들에서 서빙
    bundle_key = f"template:{filename}"
    if bundle_key in EMBEDDED_ASSETS:
        return HTMLResponse(content=EMBEDDED_ASSETS[bundle_key])
        
    return HTMLResponse(content=f"<h3>문무대교회: {filename} 페이지를 불러올 수 없습니다.</h3>", status_code=404)

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse, include_in_schema=False)
async def home_page():
    return render_html_page("index.html")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "church": "육군학생군사학교 문무대교회", "platform": "Vercel"}

@app.get("/counseling", response_class=HTMLResponse)
async def counseling_page():
    return render_html_page("counseling.html")

@app.get("/events", response_class=HTMLResponse)
async def events_page():
    return render_html_page("events.html")

@app.get("/consolation", response_class=HTMLResponse)
async def consolation_page():
    return render_html_page("consolation.html")

@app.get("/virtual-space", response_class=HTMLResponse)
async def virtual_space_page():
    return render_html_page("virtual_space.html")

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    return render_html_page("about.html")

@app.get("/donation", response_class=HTMLResponse)
async def donation_page():
    return render_html_page("donation.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return render_html_page("admin.html")

@app.on_event("startup")
def on_startup():
    try:
        init_db()
        from app.seed_data import seed
        seed()
    except Exception as e:
        print(f"[Startup Warning] {e}")
