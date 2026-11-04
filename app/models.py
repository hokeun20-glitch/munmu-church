from pydantic import BaseModel, EmailStr
from typing import Optional, List

# 상담 모델
class CounselingRequestCreate(BaseModel):
    slot_id: Optional[int] = None
    date: str
    time_slot: str
    name: str
    phone: str
    email: Optional[str] = None
    affiliation: Optional[str] = None  # 예: 학군 64기 2대대, 00중대 기간병 등
    category: str                      # 진로, 군생활, 신앙, 대인관계, 기타
    message: str
    is_anonymous: bool = False
    secret_code: Optional[str] = None  # 비밀상담 4자리 핀번호

class CounselingCheck(BaseModel):
    name: str
    secret_code: str

# 행사 참가 신청 모델
class EventRegistrationCreate(BaseModel):
    event_id: int
    name: str
    phone: str
    affiliation: Optional[str] = None
    rank_or_role: Optional[str] = None
    companions_count: int = 0
    memo: Optional[str] = None

# 위문 신청 모델
class ConsolationRequestCreate(BaseModel):
    group_name: str
    leader_name: str
    leader_phone: str
    leader_email: Optional[str] = None
    visit_date: str
    visit_time: str
    num_attendees: int
    items_summary: Optional[str] = None
    vehicle_numbers: Optional[str] = None
    purpose: Optional[str] = None

# 후원금 입금 알림 모델
class DonationNotifyCreate(BaseModel):
    donor_name: str
    amount: int
    bank: str
    purpose: str = "선교 및 사역 후원"
    phone: Optional[str] = None
    memo: Optional[str] = None
    receipt_requested: bool = False

# 훈련생 응원 편지 모델
class SupportLetterCreate(BaseModel):
    recipient_name: str
    recipient_unit: str
    sender_name: str
    sender_relation: str
    content: str
    is_private: bool = False

# 관리자 모델
class AdminLogin(BaseModel):
    username: str
    password: str

class StatusUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None
