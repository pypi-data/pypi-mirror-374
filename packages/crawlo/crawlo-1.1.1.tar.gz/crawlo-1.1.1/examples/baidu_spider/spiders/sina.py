#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-05 13:05
# @Author  :   oscar
# @Desc    :   None
"""
import time

from crawlo import Request
from crawlo.spider import Spider
from crawlo.utils.date_tools import to_datetime

from examples.baidu_spider.items import ArticleItem


class SinaSpider(Spider):
    # 获取当前时间戳，并减去 10 分钟（600 秒）
    current_time_minus_10min = int(time.time()) - 6000
    # 构造 URL
    url = f'https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&ctime={current_time_minus_10min}'

    start_urls = [url]
    name = 'sina'
    # mysql_table = 'news_10jqka'

    allowed_domains = ['*']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse, dont_filter=True)

    async def parse(self, response):
        jsonp_str = response.json()
        rows = jsonp_str.get('data', {}).get('list', [])
        for row in rows:
            article_id = row.get('id')
            title = row.get('title')
            digest = row.get('digest')
            short = row.get('short')
            detail_url = row.get('url')
            tag = row.get('tag')
            ctime = row.get('ctime')
            source = row.get('source')
            meta = {
                'article_id': article_id,
                'title': title,
                'digest': digest,
                'short': short,
                'detail_url': detail_url,
                'source': source,
                'tag': tag,
                'ctime': to_datetime(int(ctime))
            }

            yield Request(url=detail_url, callback=self.parse_detail, encoding='gbk', meta=meta)

    @staticmethod
    async def parse_detail(response):
        item = ArticleItem()
        meta = response.meta
        content = ''.join(response.xpath('//*[@id="contentApp"]/p/text()').extract()).strip()
        ctime = meta.get('ctime')
        item['article_id'] = meta.get('article_id')
        item['title'] = meta.get('title')
        item['digest'] = content
        item['short'] = meta.get('short')
        item['url'] = meta.get('detail_url')
        item['tag'] = meta.get('tag').strip()
        item['ctime'] = to_datetime(ctime)
        item['source'] = meta.get('source')

        yield item

    async def spider_opened(self):
        pass

    async def spider_closed(self):
        pass
