from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.models import AdminLogin, StatusUpdate

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ADMIN_USER = "admin"
ADMIN_PASS = "munmu1234!"

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
        
        # 1. 상담 건수
        cursor.execute("SELECT COUNT(*) FROM counseling_requests WHERE status = '신청완료'")
        pending_counseling = cursor.fetchone()[0]
        
        # 2. 위문 신청 건수
        cursor.execute("SELECT COUNT(*) FROM consolation_requests WHERE status = '대기중'")
        pending_consolations = cursor.fetchone()[0]
        
        # 3. 후원금 확인대기 건수
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM donations WHERE status = '확인대기'")
        row = cursor.fetchone()
        pending_donations = row[0]
        pending_donation_amount = row[1]
        
        # 4. 전체 행사 참가자 수
        cursor.execute("SELECT COUNT(*) FROM event_registrations")
        total_event_registrations = cursor.fetchone()[0]
        
        # 5. 최근 활동 5건
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
