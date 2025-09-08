#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-05 13:05
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio
from crawlo import Request
from crawlo.spider import Spider

from items import BauDuItem


class BaiDuSpider(Spider):
    start_urls = ["https://www.baidu.com/", "https://www.baidu.com/"]

    custom_settings = {
        'CONCURRENCY': 1
    }

    name = "bai_du"

    # headers = {
    #     "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    # }
    #
    user_gent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

    async def parse(self, response):
        for i in range(5):
            url = f"https://www.baidu.com"
            # url = f"https://www.httpbin.org/404"
            r = Request(url=url, callback=self.parse_page, dont_filter=True)
            yield r

    async def parse_page(self, response):
        for i in range(5):
            url = f"https://www.baidu.com"
            meta = {'test': 'hhhh'}
            r = Request(url=url, callback=self.parse_detail, meta=meta, dont_filter=False)
            yield r

    def parse_detail(self, response):
        item = BauDuItem()
        item['title'] = response.xpath('//title/text()').get()

        item['url'] = response.url

        yield item

    async def spider_opened(self):
        pass

    async def spider_closed(self):
        pass


if __name__ == '__main__':
    b = BaiDuSpider()
    b.start_requests()
