import sqlite3
import os
import shutil
from contextlib import contextmanager

ORIGINAL_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "munmu_church.db")

def get_database_path():
    """Vercel 서버리스(/tmp 쓰기 전용)와 로컬 환경을 모두 안전하게 지원하는 DB 경로"""
    if os.getenv("VERCEL"):
        tmp_db = "/tmp/munmu_church.db"
        if not os.path.exists(tmp_db) and os.path.exists(ORIGINAL_DB_PATH):
            try:
                shutil.copy2(ORIGINAL_DB_PATH, tmp_db)
            except Exception as e:
                print(f"[DB Copy Error] {e}")
        return tmp_db
    return ORIGINAL_DB_PATH

@contextmanager
def get_db():
    db_file = get_database_path()
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. 설교 영상
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            preacher TEXT NOT NULL,
            date TEXT NOT NULL,
            scripture TEXT NOT NULL,
            youtube_id TEXT NOT NULL,
            description TEXT,
            views INTEGER DEFAULT 0
        )
        """)
        
        # 2. 주보
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bulletins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            volume_no TEXT,
            image_url TEXT NOT NULL,
            pdf_url TEXT
        )
        """)
        
        # 3. 상담 가능 슬롯
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS counseling_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            counselor_name TEXT DEFAULT '김요한 군종목사'
        )
        """)
        
        # 4. 상담 신청
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS counseling_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_id INTEGER,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            affiliation TEXT,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            is_anonymous INTEGER DEFAULT 0,
            secret_code TEXT,
            status TEXT DEFAULT '신청완료',
            admin_notes TEXT,
            google_event_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slot_id) REFERENCES counseling_slots(id)
        )
        """)
        
        # 5. 정기 및 특별 행사
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            max_participants INTEGER DEFAULT 100,
            current_participants INTEGER DEFAULT 0,
            image_url TEXT,
            description TEXT,
            is_open INTEGER DEFAULT 1
        )
        """)
        
        # 6. 행사 참여자 접수
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            affiliation TEXT,
            rank_or_role TEXT,
            companions_count INTEGER DEFAULT 0,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
        """)
        
        # 7. 위문 신청 (일정 중복 방지 관리)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consolation_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            leader_name TEXT NOT NULL,
            leader_phone TEXT NOT NULL,
            leader_email TEXT,
            visit_date TEXT NOT NULL,
            visit_time TEXT NOT NULL,
            num_attendees INTEGER NOT NULL,
            items_summary TEXT,
            vehicle_numbers TEXT,
            purpose TEXT,
            status TEXT DEFAULT '대기중',
            admin_memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 8. 후원금 입금 알림
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            bank TEXT NOT NULL,
            purpose TEXT DEFAULT '선교/사역 후원',
            phone TEXT,
            memo TEXT,
            status TEXT DEFAULT '확인대기',
            receipt_requested INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 9. 훈련생 응원 편지 (디지털 위문편지)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_name TEXT NOT NULL,
            recipient_unit TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            sender_relation TEXT NOT NULL,
            content TEXT NOT NULL,
            is_private INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 10. 교회 연혁
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT NOT NULL,
            month TEXT,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT
        )
        """)
        
        # 11. 갤러리 (사진)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gallery_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT NOT NULL,
            date TEXT,
            description TEXT
        )
        """)
        
        # 12. 교역자 프로필
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pastors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT NOT NULL,
            image_url TEXT,
            scripture TEXT
        )
        """)
        
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
