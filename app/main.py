import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import counseling, events, consolation, donation, church_info, admin
from fastapi.responses import Response

app = FastAPI(
    title="육군학생군사학교 문무대교회",
    description="ROTC·학사장교 후보생과 국군 장병의 영적 요람, 문무대교회 공식 웹 플랫폼",
    version="1.0.0"
)

# 십자가 파비콘 SVG
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#0f1d38"/>
  <rect x="13.5" y="4" width="5" height="24" rx="1.5" fill="#f5d77f"/>
  <rect x="6" y="10" width="20" height="5" rx="1.5" fill="#f5d77f"/>
</svg>"""

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 라우터 등록
app.include_router(counseling.router)
app.include_router(events.router)
app.include_router(consolation.router)
app.include_router(donation.router)
app.include_router(church_info.router)
app.include_router(admin.router)

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/counseling", response_class=HTMLResponse)
async def counseling_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "counseling.html"))

@app.get("/events", response_class=HTMLResponse)
async def events_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "events.html"))

@app.get("/consolation", response_class=HTMLResponse)
async def consolation_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "consolation.html"))

@app.get("/virtual-space", response_class=HTMLResponse)
async def virtual_space_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "virtual_space.html"))

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "about.html"))

@app.get("/donation", response_class=HTMLResponse)
async def donation_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "donation.html"))

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "admin.html"))

@app.on_event("startup")
def on_startup():
    try:
        init_db()
        from app.seed_data import seed
        seed()
    except Exception as e:
        print(f"[Startup Warning] {e}")
