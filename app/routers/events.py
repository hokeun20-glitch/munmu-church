from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.models import EventRegistrationCreate

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("")
def list_events():
    """정기 및 특별 행사 목록"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, category, date, time, location, max_participants, current_participants, image_url, description, is_open
            FROM events
            ORDER BY date ASC
        """)
        events = [dict(row) for row in cursor.fetchall()]
        return {"events": events}

@router.get("/{event_id}")
def get_event(event_id: int):
    """행사 상세 정보"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="행사를 찾을 수 없습니다.")
        return {"event": dict(row)}

@router.post("/{event_id}/register")
def register_event(event_id: int, payload: EventRegistrationCreate):
    """행사 참여 신청 접수"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, max_participants, current_participants, is_open FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="행사를 찾을 수 없습니다.")
        
        if event["is_open"] == 0:
            raise HTTPException(status_code=400, detail="이미 마감된 행사입니다.")
        
        total_people = 1 + payload.companions_count
        if event["current_participants"] + total_people > event["max_participants"]:
            raise HTTPException(status_code=400, detail="남은 정원이 부족하여 신청할 수 없습니다.")
        
        cursor.execute("""
            INSERT INTO event_registrations 
            (event_id, name, phone, affiliation, rank_or_role, companions_count, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            payload.name,
            payload.phone,
            payload.affiliation,
            payload.rank_or_role,
            payload.companions_count,
            payload.memo
        ))
        
        # 참가자 수 업데이트
        new_count = event["current_participants"] + total_people
        is_still_open = 0 if new_count >= event["max_participants"] else 1
        cursor.execute("""
            UPDATE events 
            SET current_participants = ?, is_open = ?
            WHERE id = ?
        """, (new_count, is_still_open, event_id))
        
        conn.commit()

        return {
            "success": True,
            "message": f"'{event['title']}' 참여 신청이 정상적으로 완료되었습니다.",
            "total_registered": total_people
        }
