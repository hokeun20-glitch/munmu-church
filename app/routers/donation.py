from fastapi import APIRouter, BackgroundTasks
from app.database import get_db
from app.models import DonationNotifyCreate
from app.services.notifier import notify_new_donation
import os

router = APIRouter(prefix="/api/donations", tags=["Donations"])

OFFICIAL_ACCOUNTS = [
    {
        "bank": "농협은행",
        "account_number": "301-0284-5912-71",
        "holder": "육군학생군사학교 문무대교회",
        "description": "교회 일반 헌금 및 정기사역 후원"
    },
    {
        "bank": "국민은행",
        "account_number": "488401-01-382910",
        "holder": "육군학생군사학교 문무대교회",
        "description": "하계/동계 ROTC 후보생 훈련 위문 및 간식비 전용"
    },
    {
        "bank": "신한은행",
        "account_number": "100-032-948123",
        "holder": "육군학생군사학교 문무대교회",
        "description": "진중세례 및 군종사관 양성 장학 후원"
    }
]

@router.get("/accounts")
def get_accounts():
    """공식 후원 및 헌금 계좌 목록"""
    return {"accounts": OFFICIAL_ACCOUNTS}

@router.post("/notify")
async def notify_donation(payload: DonationNotifyCreate, background_tasks: BackgroundTasks):
    """후원금 입금 확인 알림 접수"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO donations 
            (donor_name, amount, bank, purpose, phone, memo, receipt_requested, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, '확인대기')
        """, (
            payload.donor_name,
            payload.amount,
            payload.bank,
            payload.purpose,
            payload.phone,
            payload.memo,
            1 if payload.receipt_requested else 0
        ))
        donation_id = cursor.lastrowid
        conn.commit()

        # 백그라운드 태스크로 실시간 푸시 발송
        background_tasks.add_task(
            notify_new_donation,
            donor_name=payload.donor_name,
            amount=payload.amount,
            bank=payload.bank,
            purpose=payload.purpose
        )

        return {
            "success": True,
            "message": f"{payload.donor_name}님의 따뜻한 후원 입금 알림이 담임목사님과 재정팀에 전달되었습니다. 귀한 섬김에 감사드립니다.",
            "donation_id": donation_id
        }
