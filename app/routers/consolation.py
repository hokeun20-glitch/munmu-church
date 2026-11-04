from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.models import ConsolationRequestCreate

router = APIRouter(prefix="/api/consolations", tags=["Consolations"])

@router.get("/booked-dates")
def get_booked_dates():
    """이미 확정/진행 중인 위문 일정 목록 (중복 신청 방지용 캘린더 표시)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, visit_date, visit_time, group_name, status
            FROM consolation_requests
            WHERE status IN ('승인완료', '대기중') AND visit_date >= date('now')
            ORDER BY visit_date ASC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        return {"booked_schedules": rows}

@router.post("/request")
def request_consolation(payload: ConsolationRequestCreate):
    """위문 신청 접수 (동일 일자/시간대 중복 방지 검사)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 중복 검사: 동일 날짜에 '승인완료'된 다른 위문 일정이 있는지 확인
        cursor.execute("""
            SELECT id, group_name, visit_time, status 
            FROM consolation_requests 
            WHERE visit_date = ? AND status = '승인완료'
        """, (payload.visit_date,))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"선택하신 일자({payload.visit_date})에는 이미 '{existing['group_name']}'의 위문 일정이 확정되어 있습니다. 다른 일자를 선택해 주시거나 담당자에게 문의해 주세요."
            )
            
        cursor.execute("""
            INSERT INTO consolation_requests 
            (group_name, leader_name, leader_phone, leader_email, visit_date, visit_time, num_attendees, items_summary, vehicle_numbers, purpose, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '대기중')
        """, (
            payload.group_name,
            payload.leader_name,
            payload.leader_phone,
            payload.leader_email,
            payload.visit_date,
            payload.visit_time,
            payload.num_attendees,
            payload.items_summary,
            payload.vehicle_numbers,
            payload.purpose
        ))
        req_id = cursor.lastrowid
        conn.commit()

        return {
            "success": True,
            "message": "위문 신청이 접수되었습니다. 부대 보안 규정 및 훈련 일정 검토 후 군종실에서 연락드립니다.",
            "request_id": req_id
        }
