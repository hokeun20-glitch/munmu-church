from fastapi import APIRouter
from app.database import get_db
from app.models import SupportLetterCreate

router = APIRouter(prefix="/api", tags=["Church Info"])

@router.get("/sermons")
def get_sermons():
    """설교 영상 목록"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sermons ORDER BY date DESC")
        sermons = [dict(row) for row in cursor.fetchall()]
        return {"sermons": sermons}

@router.get("/bulletins")
def get_bulletins():
    """주보 목록"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bulletins ORDER BY date DESC")
        bulletins = [dict(row) for row in cursor.fetchall()]
        return {"bulletins": bulletins}

@router.get("/history")
def get_history():
    """교회 연혁"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history_events ORDER BY year ASC, month ASC")
        history = [dict(row) for row in cursor.fetchall()]
        return {"history": history}

@router.get("/gallery")
def get_gallery():
    """시설 및 사역 갤러리 사진"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gallery_items ORDER BY id DESC")
        gallery = [dict(row) for row in cursor.fetchall()]
        return {"gallery": gallery}

@router.get("/pastors")
def get_pastors():
    """교역자 프로필"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pastors ORDER BY id ASC")
        pastors = [dict(row) for row in cursor.fetchall()]
        return {"pastors": pastors}

@router.get("/letters")
def get_letters():
    """훈련생 응원 편지 목록 (비공개 제외)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, recipient_name, recipient_unit, sender_name, sender_relation, content, created_at 
            FROM support_letters 
            WHERE is_private = 0 
            ORDER BY id DESC
        """)
        letters = [dict(row) for row in cursor.fetchall()]
        return {"letters": letters}

@router.post("/letters")
def create_letter(payload: SupportLetterCreate):
    """훈련생 응원 편지 작성"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO support_letters 
            (recipient_name, recipient_unit, sender_name, sender_relation, content, is_private)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.recipient_name,
            payload.recipient_unit,
            payload.sender_name,
            payload.sender_relation,
            payload.content,
            1 if payload.is_private else 0
        ))
        letter_id = cursor.lastrowid
        conn.commit()
        return {
            "success": True,
            "message": f"'{payload.recipient_name}' 후보생에게 응원과 기도의 마음이 안전하게 접수되었습니다. 주일 예배 시 전달됩니다.",
            "letter_id": letter_id
        }
