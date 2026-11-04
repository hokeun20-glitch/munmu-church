from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import os
import uuid
import aiofiles
from urllib.parse import quote
from app.database import get_db
from app.models import AdminLogin, StatusUpdate
from app.services.notifier import IN_MEMORY_ALERTS
from app.services.excel_exporter import export_event_registrations_to_excel, export_consolations_to_excel

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ADMIN_USER = "admin"
ADMIN_PASS = "munmu1234!"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/login")
def admin_login(payload: AdminLogin):
    """관리자 로그인"""
    if payload.username == ADMIN_USER and payload.password == ADMIN_PASS:
        return {
            "success": True,
            "token": "munmu-admin-token-secure-2026",
            "user": {
                "username": "admin",
                "name": "문무대교회 관리자",
                "role": "군종행정관"
            }
        }
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

@router.get("/dashboard")
def get_dashboard_summary():
    """관리자 메인 대시보드 요약 지표"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM counseling_requests WHERE status = '신청완료'")
        pending_counseling = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM consolation_requests WHERE status = '대기중'")
        pending_consolations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM donations WHERE status = '확인대기'")
        row = cursor.fetchone()
        pending_donations = row[0]
        pending_donation_amount = row[1]
        
        cursor.execute("SELECT COUNT(*) FROM event_registrations")
        total_event_registrations = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT '상담' as type, name as title, category as subtitle, created_at, status 
            FROM counseling_requests 
            UNION ALL
            SELECT '위문' as type, group_name as title, visit_date as subtitle, created_at, status 
            FROM consolation_requests
            UNION ALL
            SELECT '후원' as type, donor_name as title, CAST(amount as TEXT) || '원' as subtitle, created_at, status 
            FROM donations
            ORDER BY created_at DESC 
            LIMIT 6
        """)
        recent_activities = [dict(r) for r in cursor.fetchall()]

        return {
            "pending_counseling": pending_counseling,
            "pending_consolations": pending_consolations,
            "pending_donations": pending_donations,
            "pending_donation_amount": pending_donation_amount,
            "total_event_registrations": total_event_registrations,
            "recent_activities": recent_activities
        }

@router.get("/realtime-alerts")
def get_realtime_alerts():
    """대시보드 실시간 팝업 알림 폴링 API"""
    return {"alerts": IN_MEMORY_ALERTS}

@router.get("/counselings")
def get_all_counselings():
    """모든 상담 신청 내역"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM counseling_requests ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        return {"counselings": rows}

@router.patch("/counselings/{request_id}/status")
def update_counseling_status(request_id: int, payload: StatusUpdate):
    """상담 상태 및 관리자 메모 업데이트"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE counseling_requests 
            SET status = ?, admin_notes = ? 
            WHERE id = ?
        """, (payload.status, payload.admin_notes, request_id))
        conn.commit()
        return {"success": True, "message": "상담 상태가 변경되었습니다."}

@router.get("/consolations")
def get_all_consolations():
    """모든 위문 신청 내역"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consolation_requests ORDER BY visit_date ASC, id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        return {"consolations": rows}

@router.patch("/consolations/{request_id}/status")
def update_consolation_status(request_id: int, payload: StatusUpdate):
    """위문 신청 승인/반려/조율 상태 및 행정 메모 업데이트"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE consolation_requests 
            SET status = ?, admin_memo = ? 
            WHERE id = ?
        """, (payload.status, payload.admin_notes, request_id))
        conn.commit()
        return {"success": True, "message": "위문 신청 상태가 업데이트되었습니다."}

@router.get("/donations")
def get_all_donations():
    """모든 후원금 알림 내역"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donations ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        return {"donations": rows}

@router.patch("/donations/{donation_id}/confirm")
def confirm_donation(donation_id: int):
    """후원금 입금 확인 처리"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE donations SET status = '입금확인완료' WHERE id = ?", (donation_id,))
        conn.commit()
        return {"success": True, "message": "후원금 입금이 확인 완료되었습니다."}

@router.get("/events/{event_id}/registrations")
def get_event_registrations(event_id: int):
    """특정 행사의 참가자 목록"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, phone, affiliation, rank_or_role, companions_count, memo, created_at 
            FROM event_registrations 
            WHERE event_id = ? 
            ORDER BY id ASC
        """, (event_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        return {"registrations": rows}

# ==========================================
# 엑셀 다운로드 엔드포인트 (스프린트 4)
# ==========================================
@router.get("/events/{event_id}/export-excel")
def export_event_excel(event_id: int):
    """행사 참가자 명단 엑셀(.xlsx) 다운로드"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        event_title = event["title"] if event else f"행사_{event_id}"

        cursor.execute("SELECT * FROM event_registrations WHERE event_id = ? ORDER BY id ASC", (event_id,))
        attendees = [dict(r) for r in cursor.fetchall()]

    excel_stream = export_event_registrations_to_excel(event_title, attendees)
    encoded_filename = quote(f"문무대교회_{event_title}_명부.xlsx")
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

@router.get("/consolations/export-excel")
def export_consolations_excel():
    """위문 단체 및 위병소 출입 차량 명부 엑셀(.xlsx) 다운로드"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consolation_requests ORDER BY visit_date ASC, id DESC")
        rows = [dict(r) for r in cursor.fetchall()]

    excel_stream = export_consolations_to_excel(rows)
    encoded_filename = quote("문무대교회_위문출입명부.xlsx")
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

# ==========================================
# 콘텐츠 관리 (주보, 설교, 갤러리 업로드 CRUD)
# ==========================================
@router.post("/bulletins")
async def create_bulletin(
    title: str = Form(...),
    date: str = Form(...),
    volume_no: str = Form(...),
    image: UploadFile = File(None),
    image_url: str = Form(None)
):
    """새 주보 등록 (파일 업로드 또는 URL)"""
    saved_url = image_url
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"bulletin_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        async with aiofiles.open(filepath, "wb") as f:
            content = await image.read()
            await f.write(content)
        saved_url = f"/static/uploads/{filename}"

    if not saved_url:
        saved_url = "https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=1200&q=80"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bulletins (title, date, volume_no, image_url, pdf_url)
            VALUES (?, ?, ?, ?, '#')
        """, (title, date, volume_no, saved_url))
        conn.commit()
    return {"success": True, "message": "주보가 성공적으로 등록되었습니다."}

@router.delete("/bulletins/{bulletin_id}")
def delete_bulletin(bulletin_id: int):
    """주보 삭제"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bulletins WHERE id = ?", (bulletin_id,))
        conn.commit()
    return {"success": True, "message": "주보가 삭제되었습니다."}

@router.post("/sermons")
def create_sermon(
    title: str = Form(...),
    preacher: str = Form(...),
    date: str = Form(...),
    scripture: str = Form(...),
    youtube_id: str = Form(...),
    description: str = Form(...)
):
    """새 설교 등록"""
    # youtube_id에 전체 URL이 들어왔을 경우 ID만 추출
    clean_yt_id = youtube_id
    if "v=" in clean_yt_id:
        clean_yt_id = clean_yt_id.split("v=")[1].split("&")[0]
    elif "youtu.be/" in clean_yt_id:
        clean_yt_id = clean_yt_id.split("youtu.be/")[1].split("?")[0]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sermons (title, preacher, date, scripture, youtube_id, description, views)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (title, preacher, date, scripture, clean_yt_id, description))
        conn.commit()
    return {"success": True, "message": "설교 영상이 등록되었습니다."}

@router.delete("/sermons/{sermon_id}")
def delete_sermon(sermon_id: int):
    """설교 삭제"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sermons WHERE id = ?", (sermon_id,))
        conn.commit()
    return {"success": True, "message": "설교 영상이 삭제되었습니다."}

@router.post("/gallery")
async def create_gallery_item(
    title: str = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    image_url: str = Form(None)
):
    """갤러리 사진 등록 (파일 업로드 또는 이미지 URL)"""
    saved_url = image_url
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"gallery_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        async with aiofiles.open(filepath, "wb") as f:
            content = await image.read()
            await f.write(content)
        saved_url = f"/static/uploads/{filename}"

    if not saved_url:
        saved_url = "https://images.unsplash.com/photo-1548625361-195fe5795df5?auto=format&fit=crop&w=1200&q=80"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gallery_items (title, category, image_url, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (title, category, saved_url, date, description))
        conn.commit()
    return {"success": True, "message": "갤러리 사진이 등록되었습니다."}

@router.delete("/gallery/{gallery_id}")
def delete_gallery_item(gallery_id: int):
    """갤러리 사진 삭제"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gallery_items WHERE id = ?", (gallery_id,))
        conn.commit()
    return {"success": True, "message": "사진이 삭제되었습니다."}
