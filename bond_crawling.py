import json
import os
from PyPDF2 import PdfReader
import os
import requests
import json
from bs4 import BeautifulSoup
import pymysql

#PDF 다운로드
def download(url, file_path):
    with open(file_path, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

import os
import requests
from bs4 import BeautifulSoup
import pymysql
from PyPDF2 import PdfReader
import json
import sys

# 재귀 깊이 설정
sys.setrecursionlimit(1500)

# DB 접근
db = pymysql.connect(host='host',
                     port=3306, user="host", passwd="pwd",
                     db="PAPER_PROJECT_1", charset="utf8")
cursor = db.cursor()

# 다운로드 함수 정의
def download(link, file_path):
    response = requests.get(link)
    with open(file_path, 'wb') as f:
        f.write(response.content)

# 특수 문자 제거 함수 정의
def sanitize_filename(filename):
    return "".join([c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename])

# 페이지에서 각 PDF URL 전달, title, media, date 변수 설정
for i in range(101, 133): #1~132page -> 133까지
    url = f'https://finance.naver.com/research/debenture_list.naver?keyword=&brokerCode=&searchType=writeDate&writeFromDate=2008-04-01&writeToDate=2021-05-26&x=33&y=12&page={i}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    rows = soup.select('#contentarea_left > div.box_type_m > table.type_1 > tr:has(> td:nth-child(4))')

    for li in rows:
        tds = [td.text.strip() for td in li.select('td')]
        if li.select('td:nth-child(3) > a'):
            link = li.select('a')[1]['href']
        else:
            continue
        title, media, _, date, view = tds
        title = sanitize_filename(title)  # 파일 이름에서 특수 문자 제거
        print(title, media, link, date, view)

        directory = "/"  # PDF 파일 저장 경로
        file_path = os.path.join(directory, f'{title}.pdf')

        # PDF 다운로드
        try:
            download(link, file_path)
        except Exception as e:
            print(f"Failed to download {link}: {e}")
            continue

        # PDF 파일 읽기 및 텍스트 추출
        try:
            reader = PdfReader(file_path, strict=False)
            pages = reader.pages
            text = []
            for page in pages:
                try:
                    sub = page.extract_text()
                    if sub:
                        text.append(sub)
                except Exception as e:
                    print(f"Failed to extract text from {title}: {e}")
                    continue
        except RecursionError as e:
            print(f"RecursionError in file {title}: {e}")
            continue
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        # JSON 변환
        contents = {"keyword": text}
        contents = json.dumps(contents)

        # SQL에 데이터 삽입
        sql = "INSERT INTO text_analysis (document_type, date, title,media, sentences, sentiment_score_market, reg_date) VALUES (%s, %s,%s, %s, %s, %s, %s);"
        cursor.execute(sql, ('analyst_report', date, title,media, contents, 0,'2024-09-02'))
        db.commit()

db.close()
