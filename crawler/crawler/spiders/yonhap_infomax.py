import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from scrapy import Spider, Request

from ..items import YonhapNewsItem


class YonhapInfomaxSpider(Spider):
    name = "yonhap_infomax"
    allowed_domains = ["naver.com", "einfomax.co.kr"]

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'crawler.middlewares.TooManyRequestsRetryMiddleware': 543,
            'crawler.middlewares.LogRequestMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    def __init__(self, keyword='금리', start_date='2013.01.01', end_date='2024.08.31', *args, **kwargs):
        super(YonhapInfomaxSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.start_date = datetime.strptime(start_date, "%Y.%m.%d")
        self.end_date = datetime.strptime(end_date, "%Y.%m.%d")
        self.date_ranges = list(self.split_date_range(self.start_date, self.end_date))

    def split_date_range(self, start_date, end_date):
        current_start = start_date
        while current_start < end_date:
            if current_start.month == 12:
                next_month = current_start.replace(year=current_start.year + 1, month=1, day=1)
            else:
                next_month = current_start.replace(month=current_start.month + 1, day=1)
            current_end = min(next_month - timedelta(days=1), end_date)
            yield current_start, current_end
            current_start = next_month

    def start_requests(self):
        for start, end in self.date_ranges:
            url = self.get_search_url(start, end)
            self.logger.info(f"Requesting period {start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}")
            yield Request(url, callback=self.parse, meta={'start_date': start, 'end_date': end})

    def get_search_url(self, start_date, end_date):
        start_str = start_date.strftime("%Y.%m.%d")
        end_str = end_date.strftime("%Y.%m.%d")
        return f"https://search.naver.com/search.naver?where=news&query={self.keyword}&sm=tab_opt&sort=1&photo=0&field=0&pd=3&ds={start_str}&de={end_str}&docid=&related=0&mynews=1&office_type=2&office_section_code=8&news_office_checked=2227&nso=so%3Add%2Cp%3Afrom{start_str.replace('.', '')}to{end_str.replace('.', '')}&is_sug_officeid=0&office_category=0&service_area=0"

    def parse(self, response):
        for news in response.xpath("//ul[contains(@class, 'list_news')]//li//*[contains(@class, 'news_contents')]//a[contains(@class, 'news_tit')]/@href").getall():
            yield Request(news, callback=self.parse_news)

        start_date = response.meta['start_date']
        end_date = response.meta['end_date']
        next_url = self.get_next_url(start_date, end_date)
        yield Request(next_url, callback=self.parse_list, meta={'start_date': start_date, 'end_date': end_date})

    def get_next_url(self, start_date, end_date):
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        return f"https://s.search.naver.com/p/newssearch/search.naver?de={end_str}&ds={start_str}&eid=&field=0&force_original=&is_dts=0&is_sug_officeid=0&mynews=1&news_office_checked=2227&nlu_query=&nqx_theme=%7B%22theme%22%3A%7B%22main%22%3A%7B%22name%22%3A%22finance%22%7D%7D%7D&nso=%26nso%3Dso%3Add%2Cp%3Afrom{start_str}to{end_str}%2Ca%3Aall&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&office_category=0&office_section_code=8&office_type=2&pd=3&photo=0&query={self.keyword}&query_original=&service_area=0&sort=1&spq=0&start=11&where=news_tab_api&nso=so:dd,p:from{start_str}to{end_str},a:all"

    def parse_list(self, response):
        data = json.loads(response.text)
        contents = data.get("contents", [])

        for news_html in contents:
            soup = BeautifulSoup(news_html, 'html.parser')
            news_url = soup.select_one('.news_contents a.news_tit')

            if news_url.get('href'):
                yield Request(news_url['href'], callback=self.parse_news)
            else:
                self.logger.warning(f"No news URL found: {soup.select_one('.news_contents a').get('href') if soup.select_one('.news_contents a') else ''}")

        if data.get("nextUrl"):
            yield Request(data["nextUrl"], callback=self.parse_list, meta=response.meta)

    def parse_news(self, response):
        if response.status == 200:
            item = YonhapNewsItem()
            item["title"] = response.xpath('//h3[@class="heading"]/text()').get()
            item["press"] = "연합인포맥스"
            item["content"] = " ".join([' '.join(c.split()).strip() for c in response.xpath("//article[@id='article-view-content-div']//text()").getall()]).strip()
            reg_date = response.xpath("//article[1]/ul/li[2]/text()").get() if response.xpath("//article[1]/ul/li[2]/text()").get() else "1900.01.01 00:00"
            item["reg_date"] = datetime.strptime(reg_date.strip().removeprefix("입력").strip(), "%Y.%m.%d %H:%M")
            item["category"] = {k: v for k, v in parse_qs(urlparse(response.xpath('//*[@id="article-view"]/div/header/nav/ul/li[2]/a/@href').get()).query).items()}.get("sc_section_code", ["no category"])[0]
            item["url"] = response.url
            yield item
        else:
            self.logger.error(f"Failed to fetch {response.url}: HTTP status code {response.status}")
