#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-05 13:12
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio
from crawlo.crawler import CrawlerProcess

from examples.baidu_spider.spiders.miit import MiitDeviceSpider
from examples.baidu_spider.spiders.sina import SinaSpider


async def main():
    process = CrawlerProcess()
    # await process.crawl(
    #     [
    #         # SinaSpider,
    #         MiitDeviceSpider
    #     ]
    # )
    await process.crawl('miit_device')


if __name__ == '__main__':
    asyncio.run(main())
