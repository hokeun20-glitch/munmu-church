from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("<h1>문무대교회 Vercel 가동 성공!</h1>")

@app.get("/api/health")
def health():
    return {"status": "ok", "platform": "Vercel"}
