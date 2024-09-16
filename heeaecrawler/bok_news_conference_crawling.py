import os
import re
import struct
import time
import zlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import olefile
import pandas as pd


# 1. 기자간담자료 download link 구하기
def get_bok_news_conference_data(startyear, startmonth, endyear, endmonth):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)  # 최대 10초까지 대기

    result = []

    while (startyear < endyear) or (startyear == endyear and startmonth <= endmonth):
        url = f'https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755&pYear={startyear}#content'
        driver.get(url)

        # 테이블이 로드될 때까지 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#tableId > tbody > tr')))

        tr_tags = driver.find_elements(By.CSS_SELECTOR, '#tableId > tbody > tr')

        for tr_tag in tr_tags:
            day = tr_tag.find_element(By.CSS_SELECTOR, 'th').text
            month = int(day[:2])

            # 해당 월이 현재 처리하는 월인지 확인
            if month == startmonth:
                td_tag = tr_tag.find_elements(By.CSS_SELECTOR, 'td')[1]
                li_tag = td_tag.find_elements(By.CSS_SELECTOR, 'div.listText > div.fileGroupSet > div.fileGoupBox > ul > li')[0]
                a_tag = li_tag.find_element(By.CSS_SELECTOR, 'a')
                dlink = a_tag.get_attribute('href')
                title = (a_tag.get_attribute('title'))[:-4]

                result.append(dict(
                    year=startyear,
                    day=day,
                    news_conf_dlink=dlink,
                    title=title.replace('+', ' ')
                ))

        # 월을 증가시키고, 12월을 넘어가면 연도를 증가
        if startmonth == 12:
            startmonth = 1
            startyear += 1
        else:
            startmonth += 1

    driver.quit()
    return result


def convert_to_datetime(df):
    df['day'] = df['day'].str.replace('월', '').str.replace('일', '').str.split('(').str[0].str.strip()
    df['date'] = df['year'].astype(str) + ' ' + df['day']
    df['date'] = pd.to_datetime(df['date'], format='%Y %m %d')
    df = df.drop(columns=['year', 'day'])
    df = df[['date', 'title', 'news_conf_dlink']]
    return df



# 2. 다운로드 파일에 저장하기
df = pd.read_csv('bok_news_conference_data_dlinkonly.csv', encoding='utf-8-sig')

# TODO: 함수화
driver = webdriver.Chrome()

for url in df['news_conf_dlink']:
    driver.get(url)

time.sleep(20)

driver.quit()


# TODO: 함수화
# 3. filename 리스트 만들기
path = "C:/Users/kwkwo/Downloads/"
all_filenames = os.listdir(path)
hwp_files = []

for filename in all_filenames:
    if filename[-4:] == ".hwp":
        hwp_files.append(filename)


# 4. 문장 추출하기
# TODO: 함수화
# 다운로드 폴더 경로 (Windows에서는 기본적으로 사용자 폴더에 있음)
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

# .hwp 파일 목록 가져오기
hwp_files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.endswith('.hwp')]

def get_hwp_text(filename):
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()
    # print(dirs)

    # HWP 파일 검증
    if ["FileHeader"] not in dirs or \
            ["\x05HwpSummaryInformation"] not in dirs:
        raise Exception("Not Valid HWP.")

    # 문서 포맷 압축 여부 확인
    header = f.openstream("FileHeader")
    header_data = header.read()
    is_compressed = (header_data[36] & 1) == 1

    # Body Sections 불러오기
    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

    # 전체 text 추출
    text = ""
    for section in sections:
        bodytext = f.openstream(section)
        data = bodytext.read()
        if is_compressed:
            unpacked_data = zlib.decompress(data, -15)
        else:
            unpacked_data = data

        # 각 Section 내 text 추출
        section_text = ""
        i = 0
        size = len(unpacked_data)
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in [67]:
                rec_data = unpacked_data[i + 4:i + 4 + rec_len]
                section_text += rec_data.decode('utf-16')
                section_text += "\n"

            i += 4 + rec_len

        text += section_text
        text += "\n"

    return text

def extract_sentences(text):
    # Updated pattern to capture sentences starting with '□' and ending at common delimiters
    pattern = r'(?:□\s)(.*?)(?=\s□|\r|$)'

    # Extract sentences using the updated pattern
    sentences = re.findall(pattern, text, re.DOTALL)

    # Remove trailing carriage returns
    sentences = [re.split(r'\r', sentence)[0] for sentence in sentences]

    # Split sentences at punctuation marks and specific delimiters
    split_sentences = []
    for sentence in sentences:
        parts = re.split(r'(?<!\d)\.(?!\d)|(?<!\d)[!?](?!\d)|(?<!\d)\n(?!\d)', sentence)

        for part in parts:
            if part.strip():
                split_sentences.append(part.strip())

    return split_sentences

def extract_sentence(text):
    # 정규 표현식을 사용하여 [ 실물경제 ]\r\n□과 氠瑢 사이의 문장을 추출
    pattern = r'\[ 실물경제 \]\r\n□(.*?)氠瑢'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # 전체 문장에서 \r\n과 \r\n 사이에 있는 문장을 추출
        extracted_text = match.group(1)
        sub_pattern = r'\r\n(.*?)\r\n'
        sub_match = re.search(sub_pattern, extracted_text, re.DOTALL)

        if sub_match:
            return sub_match.group(1).strip()

    return None

# TODO: 함수화
original_texts = []
contents = []

for hwp in hwp_files:
    text = get_hwp_text(hwp)
    original_texts.append(text)
    result = extract_sentence(text)
    if result in original_texts:
        contents.append(result)
    contents.append(extract_sentences(text))



# TODO: 함수화
# 크롤링 실행
data = get_bok_news_conference_data(2009, 5, 2018, 1)
df = pd.DataFrame(data, columns=['year', 'day', 'title', 'news_conf_dlink'])

# 날짜 데이터 변환
df = convert_to_datetime(df)

# CSV 파일로 저장
df.to_csv('bok_news_conference_data_dlinkonly.csv', index=False, encoding='utf-8-sig')

# 5. 문장 개수 확인

df['content'] = contents
df['sent-no'] = [len(sentences) for sentences in contents]

# Calculate the total number of sentences across all HWP files
total_sentences = df['sent-no'].sum()

# Print the total number of sentences
print("Total number of sentences:", total_sentences)


# 6. csv 파일로 저장
df.to_csv('bok_news_conference_data.csv', index=False)
