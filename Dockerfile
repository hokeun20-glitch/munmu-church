# 문무대교회 웹 플랫폼 배포용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 필수 유틸리티 및 타임존 설정 (한국 시간 Asia/Seoul)
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 전체 복사
COPY . .

# 데이터베이스 디렉토리 및 포트 노출
EXPOSE 8000

# 서버 실행 (프로덕션 환경)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
