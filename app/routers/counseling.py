from fastapi import APIRouter, HTTPException, BackgroundTasks
from urllib.parse import quote
from datetime import datetime
from app.database import get_db
from app.models import CounselingRequestCreate, CounselingCheck
from app.services.notifier import notify_new_counseling
from app.services.google_calendar import create_server_calendar_event, build_google_calendar_url

router = APIRouter(prefix="/api/counseling", tags=["Counseling"])

def generate_google_calendar_link(title: str, date_str: str, time_str: str, details: str, location: str = "육군학생군사학교 문무대교회 목양실") -> str:
    """
    구글 캘린더 원클릭 추가 URL 생성
    예: date_str="2026-11-10", time_str="14:00 - 15:00 (오후)"
    """
    try:
        # 시간 파싱 (앞부분 시작 시간, 뒷부분 종료 시간)
        parts = time_str.split("-")
        start_part = parts[0].strip().replace("오전", "").replace("오후", "").replace("야간", "").strip()
        end_part = parts[1].split("(")[0].strip() if len(parts) > 1 else start_part
        
        start_dt = datetime.strptime(f"{date_str} {start_part}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date_str} {end_part}", "%Y-%m-%d %H:%M")
        
        start_iso = start_dt.strftime("%Y%m%dT%H%M00")
        end_iso = end_dt.strftime("%Y%m%dT%H%M00")
        dates_param = f"{start_iso}/{end_iso}"
    except Exception:
        # 파싱 실패시 날짜 기본값
        dates_param = date_str.replace("-", "") + "/" + date_str.replace("-", "")

    encoded_title = quote(title)
    encoded_details = quote(details)
    encoded_location = quote(location)
    
    return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={encoded_title}&dates={dates_param}&details={encoded_details}&location={encoded_location}"

@router.get("/slots")
def get_available_slots():
    """예약 가능한 상담 슬롯 목록 반환"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, time_slot, is_available, counselor_name
            FROM counseling_slots
            WHERE is_available = 1 AND date >= date('now')
            ORDER BY date ASC, time_slot ASC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        return {"slots": rows}

@router.post("/request")
async def request_counseling(payload: CounselingRequestCreate, background_tasks: BackgroundTasks):
    """상담 예약 접수 및 구글 캘린더 링크 생성"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 슬롯 유효성 검사 (슬롯 id가 전달된 경우)
        if payload.slot_id:
            cursor.execute("SELECT is_available FROM counseling_slots WHERE id = ?", (payload.slot_id,))
            slot = cursor.fetchone()
            if not slot or slot["is_available"] == 0:
                raise HTTPException(status_code=400, detail="이미 예약되었거나 유효하지 않은 상담 시간대입니다.")
        
        # 구글 캘린더 이벤트 생성 엔진 호출
        cal_title = f"[문무대교회 목양상담] {payload.name} 후보생/성도 상담"
        cal_details = f"신청자: {payload.name}\n연락처: {payload.phone}\n소속: {payload.affiliation or '미기재'}\n상담분야: {payload.category}\n내용: {payload.message}"
        cal_result = create_server_calendar_event(
            title=cal_title,
            date_str=payload.date,
            time_str=payload.time_slot,
            details=cal_details,
            attendee_email=payload.email
        )
        google_link = cal_result["html_link"]

        cursor.execute("""
            INSERT INTO counseling_requests 
            (slot_id, date, time_slot, name, phone, email, affiliation, category, message, is_anonymous, secret_code, google_event_link, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '신청완료')
        """, (
            payload.slot_id,
            payload.date,
            payload.time_slot,
            payload.name,
            payload.phone,
            payload.email,
            payload.affiliation,
            payload.category,
            payload.message,
            1 if payload.is_anonymous else 0,
            payload.secret_code,
            google_link
        ))
        request_id = cursor.lastrowid

        # 해당 슬롯 예약 불가 처리
        if payload.slot_id:
            cursor.execute("UPDATE counseling_slots SET is_available = 0 WHERE id = ?", (payload.slot_id,))
            
        conn.commit()

        # 백그라운드 실시간 알림 발송
        background_tasks.add_task(
            notify_new_counseling,
            name=payload.name,
            category=payload.category,
            date=payload.date,
            time_slot=payload.time_slot,
            is_anonymous=payload.is_anonymous
        )

        return {
            "success": True,
            "message": "상담 신청이 성공적으로 접수되었습니다. 군종목사님께서 검토 후 연락드립니다.",
            "request_id": request_id,
            "google_calendar_url": google_link,
            "date": payload.date,
            "time_slot": payload.time_slot
        }

@router.post("/check")
def check_counseling_status(payload: CounselingCheck):
    """비밀 상담 내역 확인 (이름 + 4자리 비밀코드)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, time_slot, name, category, status, admin_notes, created_at
            FROM counseling_requests
            WHERE name = ? AND secret_code = ?
            ORDER BY id DESC
            LIMIT 1
        """, (payload.name, payload.secret_code))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="일치하는 상담 신청 내역을 찾을 수 없습니다. 이름과 비밀코드를 확인해주세요.")
        
        return {"counseling": dict(row)}
