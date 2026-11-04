import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 알림 설정 로드
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# 관리자 대시보드 실시간 폴링용 인메모리 알림 큐 (최신 30건)
IN_MEMORY_ALERTS = []

async def send_telegram_message(message: str) -> bool:
    """텔레그램 봇으로 관리자 스마트폰에 즉각 푸시 알림 발송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        # 콘솔 출력 시 Windows cp949 인코딩 안전 처리
        try:
            print(f"[Notifier/Console] {message}")
        except Exception:
            safe_msg = message.encode('cp949', errors='replace').decode('cp949')
            print(f"[Notifier/Console] {safe_msg}")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            return resp.status_code == 200
    except Exception as e:
        print(f"[Notifier Error] Telegram send failed: {e}")
        return False

def record_alert(alert_type: str, title: str, details: str):
    """대시보드 실시간 팝업을 위한 알림 큐 기록"""
    alert = {
        "id": len(IN_MEMORY_ALERTS) + 1,
        "type": alert_type, # 'donation', 'counseling', 'consolation'
        "title": title,
        "details": details,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    IN_MEMORY_ALERTS.insert(0, alert)
    if len(IN_MEMORY_ALERTS) > 30:
        IN_MEMORY_ALERTS.pop()

async def notify_new_donation(donor_name: str, amount: int, bank: str, purpose: str):
    """후원금 입금 알림 통합 발송"""
    title = f"후원금 입금 알림 ({donor_name} 성도님)"
    details = f"금액: {amount:,}원 | 은행: {bank} | 목적: {purpose}"
    
    record_alert("donation", title, details)
    
    tg_msg = (
        f"<b>[문무대교회 헌금/후원 알림]</b>\n"
        f"- 입금자: <b>{donor_name}</b>\n"
        f"- 후원액: <b>{amount:,}원</b>\n"
        f"- 입금은행: {bank}\n"
        f"- 후원목적: {purpose}\n"
        f"- 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await send_telegram_message(tg_msg)

async def notify_new_counseling(name: str, category: str, date: str, time_slot: str, is_anonymous: bool):
    """새로운 목양상담 접수 알림"""
    anon_str = " (익명/비밀상담)" if is_anonymous else ""
    title = f"신규 목양상담 접수 ({name}{anon_str})"
    details = f"분야: {category} | 일시: {date} {time_slot}"
    
    record_alert("counseling", title, details)
    
    tg_msg = (
        f"<b>[문무대교회 목양상담 접수]</b>\n"
        f"- 신청자: <b>{name}{anon_str}</b>\n"
        f"- 상담분야: {category}\n"
        f"- 희망일시: {date} {time_slot}\n"
        f"관리자 포털에서 확인 후 상담을 확정해 주세요."
    )
    await send_telegram_message(tg_msg)

async def notify_new_consolation(group_name: str, leader: str, visit_date: str, count: int):
    """새로운 외부 위문 신청 알림"""
    title = f"외부 위문 신청 접수 ({group_name})"
    details = f"방문일: {visit_date} | 인원: {count}명 | 대표: {leader}"
    
    record_alert("consolation", title, details)
    
    tg_msg = (
        f"<b>[문무대교회 외부위문 신청]</b>\n"
        f"- 단체명: <b>{group_name}</b>\n"
        f"- 대표자: {leader}\n"
        f"- 방문일자: {visit_date}\n"
        f"- 방문인원: {count}명\n"
        f"부대 일정 중복 여부를 확인해 주십시오."
    )
    await send_telegram_message(tg_msg)
