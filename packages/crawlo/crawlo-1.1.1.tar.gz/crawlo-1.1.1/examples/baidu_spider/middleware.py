#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-05-17 11:21
# @Author  :   crawl-coder
# @Desc    :   None
"""
import asyncio
import random

from crawlo.exceptions import IgnoreRequestError
from crawlo.middleware import BaseMiddleware


class TestMiddleWare(BaseMiddleware):

    async def process_request(self, request, spider):
        # 请求预处理
        # print('process_request', request, spider)
        # if random.randint(1, 5) == 1:
        #     raise IgnoreRequestError('url不正确')
        pass

    def process_response(self, request, response, spider):
        # 响应预处理
        # print('process_response', response, response, spider)
        return response

    def process_exception(self, request, exception, spider):
        # 异常预处理
        # print('process_exception', request, exception, spider)
        pass


class TestMiddleWare2(BaseMiddleware):
    def process_request(self, request, spider):
        # 请求预处理
        # print('process_request2', request, spider)
        pass

    def process_response(self, request, response, spider):
        # 响应预处理
        # print('process_response2', response, response, spider)
        return response

    def process_exception(self, request, exception, spider):
        # 异常预处理
        # print('process_exception2', request, exception, spider)
        pass
