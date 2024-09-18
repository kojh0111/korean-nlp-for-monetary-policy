import requests
from bs4 import BeautifulSoup
import pandas as pd

response = requests.get('https://www.edaily.co.kr/search/news/?source=total&keyword=%ed%99%98%ec%9c%a8&include=&exclude=&jname=&start=20240901&end=20240903&sort=latest&date=pick&exact=false&page=1')

soup = BeautifulSoup(response.text, 'html.parser')


title = soup.select_one('#newsList li').text
# 제목 태그 확인 

contents = soup.select('ul.newsbox_texts li')
# 기사 태그 확인 

date_range = pd.date_range('2023-01-01', '2024-8-31', freq='D')
keyword = '환율'
# 하루에 하나씩 날짜 출력
dates = []

single_date = []
urls = []
for date in date_range:
    single_date = date.strftime('%Y%m%d')
    urls.append(f'https://www.edaily.co.kr/search/news/?source=total&keyword={keyword}&include=&exclude=&jname=&start={single_date}&end={single_date}&sort=latest&date=pick&exact=false&page=')


f_urls = []
for url in urls:
    page = 1
    while True:
        current_url = url + str(page)
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cont = soup.select('ul.newsbox_texts li')
        if len(cont) == 0:
            break
        f_urls.append(current_url)
        page += 1

contents = []
reg_date = []
for url in f_urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cont = soup.select('ul.newsbox_texts li')
    date = soup.select('div.author_category')
    contents.extend(cont)
    reg_date.extend(date)

    
        
titles = []
articles = []

num = 0
for ct in contents:
    if num % 2 == 0:
        titles.extend(ct)
            
    else:
        articles.extend(ct)
    num += 1

tmp_articles = []
for art in articles:
    tmp_articles.append(art.text.split('기자]',1)[-1])


n = 0
f_reg_date = []
for dt in reg_date:
    f_reg_date.append(dt.text.split('\r\n')[1].strip())

# open_url = soup.select('#newsList a')
# f_open_url = []
# for ou in open_url:
#     f_open_url.append(ou.attrs['href'])


# 만약 길이가 다르면, 길이를 맞추기 위해 추가적인 작업이 필요함
# 예를 들어, 짧은 리스트에 None을 추가

print('length_titles:',len(titles))
print('reg_date',len(f_reg_date))
print('articles',len(tmp_articles))


min_length = min(len(titles), len(f_reg_date), len(tmp_articles))

titles = titles[:min_length]
f_reg_date = f_reg_date[:min_length]
tmp_articles = tmp_articles[:min_length]

# # 그 다음 데이터 프레임을 생성
data = {'titles': titles, 'media':'이데일리', 'reg_date': f_reg_date, 'article' : tmp_articles }

df = pd.DataFrame(data)


# 날자 조정하여 여러개 데이터 프레임 파일 만들어 합치기    
list = [df2005,df2006, df2007,df2008, df2009_10, df2011_12, df2013_14, df2015_16, df2017_18, df2019_20, df2021_22, df2023_24]


# 여러개의 데이터 프레임을 Concat 하나의 데이터 프레임으로 
edaily_df = pd.concat(list, axis = 0, ignore_index = True)

#json 파일로 저장
edaily_df.to_json('edaily_2005_24.json')
#csv 파일로 저장
edaily_df.to_csv('edaily_2005_24.csv')