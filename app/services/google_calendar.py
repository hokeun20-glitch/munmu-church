import os
from urllib.parse import quote
from datetime import datetime

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "service_account.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

def is_google_api_configured() -> bool:
    """실제 구글 클라우드 서비스 계정 키 파일 존재 여부 확인"""
    return os.path.exists(SERVICE_ACCOUNT_FILE)

def build_google_calendar_url(title: str, date_str: str, time_str: str, details: str, location: str = "문무대교회 목양실") -> str:
    """신청자 및 교역자 원클릭 구글 캘린더 웹 등록 URL 생성기"""
    try:
        parts = time_str.split("-")
        start_part = parts[0].strip().replace("오전", "").replace("오후", "").replace("야간", "").strip()
        end_part = parts[1].split("(")[0].strip() if len(parts) > 1 else start_part
        
        start_dt = datetime.strptime(f"{date_str} {start_part}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date_str} {end_part}", "%Y-%m-%d %H:%M")
        
        dates_param = f"{start_dt.strftime('%Y%m%dT%H%M00')}/{end_dt.strftime('%Y%m%dT%H%M00')}"
    except Exception:
        dates_param = date_str.replace("-", "") + "/" + date_str.replace("-", "")

    return (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(title)}"
        f"&dates={dates_param}"
        f"&details={quote(details)}"
        f"&location={quote(location)}"
    )

def create_server_calendar_event(title: str, date_str: str, time_str: str, details: str, attendee_email: str = None) -> dict:
    """
    서버 백그라운드 구글 캘린더 이벤트 생성 엔진
    Service Account 키가 있으면 구글 클라우드 API 호출, 없으면 시뮬레이션 및 웹 URL 반환
    """
    web_url = build_google_calendar_url(title, date_str, time_str, details)
    
    if is_google_api_configured():
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('calendar', 'v3', credentials=creds)

            # 시간 계산
            parts = time_str.split("-")
            start_p = parts[0].strip().replace("오전", "").replace("오후", "").replace("야간", "").strip()
            end_p = parts[1].split("(")[0].strip() if len(parts) > 1 else start_p
            start_iso = f"{date_str}T{start_p}:00+09:00"
            end_iso = f"{date_str}T{end_p}:00+09:00"

            event_body = {
                'summary': title,
                'location': '육군학생군사학교 문무대교회 2층 목양실',
                'description': details,
                'start': {'dateTime': start_iso, 'timeZone': 'Asia/Seoul'},
                'end': {'dateTime': end_iso, 'timeZone': 'Asia/Seoul'},
            }
            if attendee_email:
                event_body['attendees'] = [{'email': attendee_email}]

            created = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
            return {
                "success": True,
                "mode": "google_api_live",
                "event_id": created.get('id'),
                "html_link": created.get('htmlLink', web_url),
                "web_url": web_url
            }
        except Exception as e:
            print(f"[Google Calendar API Error] {e}")

    # 기본 모드: 즉시 등록 웹 URL 반환
    return {
        "success": True,
        "mode": "web_url_ready",
        "event_id": f"evt-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "html_link": web_url,
        "web_url": web_url
    }
