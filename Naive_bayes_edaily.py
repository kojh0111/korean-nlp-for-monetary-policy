import pickle
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd


okt = Okt()


# 샘플 데이터 (문서와 레이블)
documents = [
    '이 영화 정말 재미있다', 
    '이 영화 정말 지루하다', 
    '이 영화는 완전 감동적이다', 
    '이 영화 정말 별로다', 
    '이 영화는 시간 낭비다'
]
labels = [1, 0, 1, 0, 0]  # 1: 긍정, 0: 부정

# 데이터프레임 불러오기
df = pd.read_csv('edaily_0524.csv')

# 형태소 분석하여 명사(Noun)와 형용사('Adjective')를 추출하여 토큰화 함
def tokenize_korean(doc):
    return ' '.join([word for word, pos in okt.pos(doc) if pos in ['Noun', 'Adjective']])

# 데이터 프레임의 title열을 명사와 형용사를 추출하여 토큰화
tokenize_korean_title_list = [tokenize_korean(doc) for doc in df['title']]

# 데이터 프레임의 sentences열을 명사와 형용사를 추출하여 토큰화
tokenize_korean_contents_list = [tokenize_korean(doc) for doc in df['sentences']]


# 결과물을 데이터프레임화 하여 json파일로 저장
tkcl_df = pd.DataFrame(tokenize_korean_contents_list, columns=['sentences'])
tkcl_df.to_json('tkcl_df.json')


# BOW(Back of Words)모델을 위한 Countvectorizer 초기화
#  tokenize_korean_contents_list 변수를 Countvectorizer를 적용하여 X변수에 저장

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(tokenize_korean_contents_list)

X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.20, random_state=42)



# nb_model.pkl로 모델 저장
with open('nb_model.pkl', 'wb') as file:
    pickle.dump((model, vectorizer), file)

print(f"모델이 {model_filename} 파일로 저장되었습니다.")

# 저장된 모델 불러오기 및 사용
with open('nb_model.pkl', 'rb') as file:
    loaded_model, loaded_vectorizer = pickle.load(file)



