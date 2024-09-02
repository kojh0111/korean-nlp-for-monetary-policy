FROM python:3.12

WORKDIR /app

# 필요한 파일들을 컨테이너로 복사
COPY requirements.txt .
COPY crawler /app/crawler
COPY crawler/scrapy.cfg /app/scrapy.cfg
COPY scrapyd-data /app/scrapyd-data

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# Scrapyd 설치
RUN pip install scrapyd

# 필요한 포트 열기
EXPOSE 6800

# Scrapyd 실행
CMD ["scrapyd"]
