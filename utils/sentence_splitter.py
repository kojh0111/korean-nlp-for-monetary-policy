import re

#문장분리기
def sen_split(text):
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', str(text))

#정규 표현식으로 필요없는 부분 제거
def tokenize_korean_text(text):
    patterns = [
        r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',  # E-mail
        r'(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',  # URL
        r'<[^>]*>',  # HTML tags
        r'([ㄱ-ㅎㅏ-ㅣ]+)',  # Korean consonants and vowels
        r'([가-힣A-Za-z·\d~\-\.]{2,}(로|길)+)',  # Address patterns
        r'([가-힣A-Za-z·\d~\-\.]+(읍|동|번지|시|구)+)',
        r'([가-힣A-Za-z]+(구)\s*[가-힣A-Za-z]+(동))',
        r'([가-힣a-zA-Z\d]+(아파트|빌라|빌딩|마을))',
        r'\n',  # 줄바꿈 제거
        r'[`~!@#$%^&*()_|+\-=?;:,.<>\{\}\[\]\\\/]',  # Special characters
        r'[0-9]'  # Numbers
        r'[^a-zA-Z0-9가-힣]' # 특수문자
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)
    return text

#각 문서에 대해 문장 분리 및 정규표현식 진행
def start_split_sentences(text):
    sentences = sen_split(text)
    return [tokenize_korean_text(sentence) for sentence in sentences]

