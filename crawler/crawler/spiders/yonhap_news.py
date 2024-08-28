import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from scrapy import Spider, Request

from ..items import YonhapNewsItem


class YonhapNewsSpider(Spider):
    name = "yonhap_news"
    allowed_domains = ["naver.com"]

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

    def __init__(self, keyword='금리', start_date='2005.01.01', end_date='2017.12.31', *args, **kwargs):
        super(YonhapNewsSpider, self).__init__(*args, **kwargs)
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
        return f"https://search.naver.com/search.naver?where=news&query={self.keyword}&sm=tab_opt&sort=1&photo=0&field=0&pd=3&ds={start_str}&de={end_str}&docid=&related=0&mynews=1&office_type=2&office_section_code=8&news_office_checked=1001&nso=so%3Add%2Cp%3Afrom{start_str.replace('.', '')}to{end_str.replace('.', '')}&is_sug_officeid=0&office_category=0&service_area=0"

    def parse(self, response):
        for news in response.xpath("//ul[contains(@class, 'list_news')]//li//*[contains(@class, 'info_group')]//a[not(contains(@class, 'press'))]/@href").getall():
            yield Request(news, callback=self.parse_news)

        start_date = response.meta['start_date']
        end_date = response.meta['end_date']
        next_url = self.get_next_url(start_date, end_date)
        if next_url:
            yield Request(next_url, callback=self.parse_list, meta={'start_date': start_date, 'end_date': end_date})

    def get_next_url(self, start_date, end_date):
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        return f"https://s.search.naver.com/p/newssearch/search.naver?de={end_str}&ds={start_str}&eid=&field=0&force_original=&is_dts=0&is_sug_officeid=0&mynews=1&news_office_checked=1001&nlu_query=&nqx_theme=%7B%22theme%22%3A%7B%22main%22%3A%7B%22name%22%3A%22finance%22%7D%7D%7D&nso=%26nso%3Dso%3Add%2Cp%3Afrom{start_str}to{end_str}%2Ca%3Aall&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&office_category=0&office_section_code=8&office_type=2&pd=3&photo=0&query={self.keyword}&query_original=&service_area=0&sort=1&spq=0&start=51&where=news_tab_api&nso=so:dd,p:from{start_str}to{end_str},a:all"

    def parse_list(self, response):
        data = json.loads(response.text)
        contents = data.get("contents", [])

        for news_html in contents:
            soup = BeautifulSoup(news_html, 'html.parser')
            news_url = soup.select_one('.info_group a:not(.press)')

            if news_url.get('href'):
                yield Request(news_url['href'], callback=self.parse_news)
            else:
                self.logger.warning(f"No news URL found: {soup.select_one('.news_contents a').get('href') if soup.select_one('.news_contents a') else ''}")

        if data.get("nextUrl"):
            yield Request(data["nextUrl"], callback=self.parse_list, meta=response.meta)

    def parse_news(self, response):
        if response.status == 200:
            item = YonhapNewsItem()
            item["title"] = response.xpath("//h2[@id='title_area']/span/text()").get()
            item["press"] = response.xpath("//*[contains(@class, 'media_end_head_top_logo_img')]/@alt").get()
            item["content"] = " ".join([' '.join(c.split()).strip() for c in response.xpath("//article//text()").getall()]).strip()
            item["reg_date"] = datetime.strptime(response.xpath("//span[contains(@class, 'media_end_head_info_datestamp_time')]/@data-date-time").get(), "%Y-%m-%d %H:%M:%S")
            item["category"] = {k: v for k, v in parse_qs(urlparse(response.url).query).items()}.get("sid", ["no category"])[0]
            item["url"] = response.url
            yield item
        else:
            self.logger.error(f"Failed to fetch {response.url}: HTTP status code {response.status}")
