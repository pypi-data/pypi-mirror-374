#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-08-22 14:00
# @Author  :   oscar
# @Desc    :   爬取工信部无线电设备核准信息（支持全量34652页）
"""

import json
import asyncio
import random

from crawlo import Request
from crawlo.spider import Spider
from crawlo.utils.log import get_logger
from crawlo.utils.date_tools import to_datetime

# 引入定义好的 Item
from examples.baidu_spider.items import MiitDeviceItem


logger = get_logger(__name__)


class MiitDeviceSpider(Spider):
    name = 'miit_device'
    allowed_domains = ['ythzxfw.miit.gov.cn']

    # 字段映射表
    FIELD_MAPPING = {
        "articleField01": ("核准证编号", "approval_certificate_no"),
        "articleField02": ("设备名称", "device_name"),
        "articleField03": ("设备型号", "model_number"),
        "articleField04": ("申请单位", "applicant"),
        "articleField05": ("备注", "remarks"),
        "articleField06": ("有效期", "validity_period"),
        "articleField07": ("频率容限", "frequency_tolerance"),
        "articleField08": ("频率范围", "frequency_range"),
        "articleField09": ("发射功率", "transmission_power"),
        "articleField10": ("占用带宽", "occupied_bandwidth"),
        "articleField11": ("杂散发射限制", "spurious_emission_limit"),
        "articleField12": ("发证日期", "issue_date"),
        "articleField13": ("核准代码", "approval_code"),
        "articleField14": ("CMIIT ID", "cmiit_id"),
        "articleField15": ("调制方式", "modulation_scheme"),
        "articleField16": ("技术体制/功能模块", "technology_module"),
        "createTime": ("createTime", "create_time"),
        "articleId": ("articleId", "article_id")
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Authorization": "null",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://ythzxfw.miit.gov.cn",
        "Pragma": "no-cache",
        "Referer": "https://ythzxfw.miit.gov.cn/oldyth/resultQuery",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }

    cookies = {
        "wzws_sessionid": "gjdjYmMyNYFkZjRiZjCgaKkOx4AyNDBlOjQ3ZTozMmUwOmQ5MmI6ZjFjZTphNWJiOjk5ZmU6OTU4OQ==",
        "ariauseGraymode": "false",
        "Hm_lvt_a73626d298a849004aacc34159f68abd": "1755909833",
        "Hm_lpvt_a73626d298a849004aacc34159f68abd": "1755909833",
        "HMACCOUNT": "6C5E4C6C47DC62FF"
    }

    # 分页配置
    start_page = 1           # 起始页
    end_page = 34652         # 总页数
    current_page = 1
    page_size = 5            # 每页条数

    # 请求间隔（秒），防止被封
    min_delay = 1.5
    max_delay = 3.0

    def start_requests(self):
        # 从起始页开始
        yield self.make_request(self.start_page)

    def make_request(self, page):
        """封装请求创建"""
        data = {
            "categoryId": "352",
            "currentPage": page,
            "pageSize": self.page_size,
            "searchContent": ""
        }
        return Request(
            method='POST',
            url='https://ythzxfw.miit.gov.cn/oldyth/user-center/tbAppSearch/selectResult',
            headers=self.headers,
            cookies=self.cookies,
            body=json.dumps(data, separators=(',', ':'), ensure_ascii=False),
            callback=self.parse,
            dont_filter=True,
            meta={'page': page}  # 记录当前页码，便于日志和调试
        )

    async def parse(self, response):
        page = response.meta.get('page', 'unknown')
        try:
            json_data = response.json()
            success = json_data.get("success")
            code = json_data.get("code")

            if not success or code != 200:
                logger.error(f"第 {page} 页请求失败: code={code}, msg={json_data.get('msg')}")
                return

            tb_app_article = json_data.get('params', {}).get('tbAppArticle', {})
            records = tb_app_article.get('list', [])
            total_count = tb_app_article.get('total', 0)  # 总数据条数，例如 173256

            logger.info(f"✅ 第 {page} 页解析成功，共 {len(records)} 条数据。总计: {total_count} 条")

            for raw_item in records:
                item = MiitDeviceItem()
                for field_key, (chinese_name, english_field) in self.FIELD_MAPPING.items():
                    value = raw_item.get(field_key)
                    if english_field == 'issue_date' and value:
                        value = to_datetime(value.split()[0])
                    item[english_field] = value
                yield item

            # ✅ 核心修复：根据 total_count 和 page_size 计算真实总页数
            # 注意：需要向上取整，例如 173256 / 5 = 34651.2，应该有 34652 页
            import math
            calculated_total_pages = math.ceil(total_count / self.page_size)

            # 现在使用 calculated_total_pages 来判断是否继续翻页
            next_page = page + 1
            if next_page <= calculated_total_pages:
                delay = random.uniform(self.min_delay, self.max_delay)
                logger.debug(f"等待 {delay:.2f}s 后请求第 {next_page} 页...")
                await asyncio.sleep(delay)
                yield self.make_request(next_page)
            else:
                logger.info(f"🎉 爬取完成！已到达最后一页 {calculated_total_pages}")

        except Exception as e:
            logger.error(f"❌ 解析第 {page} 页失败: {e}, 响应: {response.text[:500]}...")

    async def spider_opened(self):
        logger.info(f"MiitDeviceSpider 启动，准备爬取 {self.start_page} 至 {self.end_page} 页...")

    async def spider_closed(self):
        logger.info("MiitDeviceSpider 结束。")