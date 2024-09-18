import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import olefile
import zlib
import struct
import re

def get_hwp_data(startyear, startmonth, endyear, endmonth):
    driver = webdriver.Chrome()
    
    result = []

    try:
        while startyear <= endyear:
            url = f'https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755&pYear={startyear}#content'
            driver.get(url)
            time.sleep(3)
            
            tr_tags = driver.find_elements(By.CSS_SELECTOR, '#tableId > tbody > tr')
            
            for tr_tag in tr_tags:
                day = tr_tag.find_element(By.CSS_SELECTOR,'th').text
                month = int(day[:2])

                if startyear == 2005 and month < startmonth:
                    continue
                if endyear == 2012 and month > endmonth:
                    break

                td_tag = tr_tag.find_elements(By.CSS_SELECTOR,'td')[2]
                if startyear == 2006 or (startyear == 2007) & (month == 1):
                    li_tag = td_tag.find_elements(By.CSS_SELECTOR,'div.fileGroupSet>div.fileGoupBox>ul>li')[1]
                    a_tag = li_tag.find_element(By.CSS_SELECTOR,'a')
                    dlink = a_tag.get_attribute('href')
                    title = (a_tag.get_attribute('title'))[:-4]
                else:
                    a_tag = td_tag.find_element(By.CSS_SELECTOR,'div.fileGroupSet>div.fileGoupBox>ul>li>a')
                    dlink = a_tag.get_attribute('href')
                    if (startyear == 2008) & (month >= 11) or startyear >= 2009:
                        title = f'{startyear}년+{(a_tag.get_attribute("title"))[:-4]}'
                    elif (startyear == 2008) & (month == 10):
                        title = '2008년+제20차+금통위+의사록'
                    elif (startyear == 2007) and (month == 2 or month == 4 or month == 7):
                        title = (a_tag.get_attribute('title'))[:-8]
                    else:
                        title = (a_tag.get_attribute('title'))[:-4]
                result.append(dict(
                    year = startyear,
                    day = day,
                    dlink = dlink,
                    title = title.replace('+', ' ')
                ))

            startyear += 1
            
    finally:
        driver.quit()

    return result

def convert_to_datetime(df):
    # 'day' 컬럼에서 "월"과 "일" 부분 제거
    df['day'] = df['day'].str.replace('월', '').str.replace('일', '').str.split('(').str[0].str.strip()
    
    # 'year'와 'day'를 합쳐서 새로운 컬럼 'date' 생성
    df['date'] = df['year'].astype(str) + ' ' + df['day']
    
    # 'date' 컬럼을 datetime 타입으로 변환
    df['date'] = pd.to_datetime(df['date'], format='%Y %m %d')
    
    # 'year'와 'day' 컬럼 제거
    df = df.drop(columns=['year', 'day'])
    
    # 열 순서를 변경하여 'date'가 먼저 오도록 설정
    df = df[['date', 'title', 'dlink']]
    
    return df

# '통화정책방향〉' ~ '(４) 심의결과' 사이의 내용만 가져오는 함수
def extract_text_after_keyword(text):
    start_keyword = "통화정책방향〉"
    end_keyword = "(４) 심의결과"
    
    if start_keyword in text:
        # '통화정책방향〉' 이후의 텍스트만 추출
        extracted_text = text.split(start_keyword, 1)[1].strip()
        
        if end_keyword in extracted_text:
            # '(４) 심의결과' 이전의 텍스트만 반환
            extracted_text = extracted_text.split(end_keyword, 1)[0].strip()
        
        return extracted_text
    
    # 키워드가 없으면 빈 문자열 반환
    return ""

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

if __name__ == '__main__':

    # 1. 의사록 다운로드 링크 불러오기
    data = get_hwp_data(2005, 5, 2017, 12)
    df = pd.DataFrame(data, columns=['year', 'day', 'title', 'dlink'])

    df = convert_to_datetime(df)

    # 2. 다운로드 파일에 저장하기

    driver = webdriver.Chrome()

    for i in df['dlink']:
        driver.get(i)

    time.sleep(20)

    driver.quit()

    # 3. filename 리스트 만들기

    path = "C:/Users/kwkwo/Downloads/"
    all_filenames = os.listdir(path)
    hwp_files = []

    for filename in all_filenames:
        if filename[-4:] == ".hwp":
            hwp_files.append(filename)

    # 4. 텍스트 가져오기

    # 다운로드 폴더 경로 (Windows에서는 기본적으로 사용자 폴더에 있음)
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # .hwp 파일 목록 가져오기
    hwp_files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.endswith('.hwp')]

    # 리스트 초기화
    contents = []

    for hwp in hwp_files:
        # print(hwp)
        text = get_hwp_text(hwp)
        contents.append(text)

    # 텍스트 정제
    extracted_contents = [extract_text_after_keyword(text) for text in contents]

    content_as_list = []
    sent_no = []

    for content in extracted_contents:
        sentences = content.split('\r\n')
        sents_as_list = []
        
        for sent in sentences:
            sent = sent.strip()
            
            # 소수점 숫자가 아닌 마침표(.)나 세미콜론(;) 기준으로 분리
            split_sentences = re.split(r'(?<!\d)\.(?!\d)|;', sent)
            
            for split_sent in split_sentences:
                split_sent = split_sent.strip()
                
                # "(３) 위원 토의내용" 제외
                if split_sent and split_sent != "(３) 위원 토의내용":
                    sents_as_list.append(split_sent)
        
        content_as_list.append(sents_as_list)
        sent_no.append(len(sents_as_list))

    df['content'] = content_as_list
    df['sent-no'] = sent_no

    # 5. csv 파일로 저장
    df.to_csv('bok_mpc_minutes_data(edited).csv')
    

