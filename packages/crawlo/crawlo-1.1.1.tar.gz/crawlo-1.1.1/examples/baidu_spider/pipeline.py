#!/usr/bin/python
# -*- coding:UTF-8 -*-
import pymongo

from motor.motor_asyncio import AsyncIOMotorClient

from random import randint

from crawlo.event import spider_closed
from crawlo.exceptions import ItemDiscard
from crawlo.utils.log import get_logger


class TestPipeline(object):

    async def process_item(self, item, spider):
        if randint(1, 3) == 1:
            raise ItemDiscard('重复数据')
        return item

    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls()


class MongoPipeline(object):

    def __init__(self, conn, col):
        self.conn = conn
        self.col = col

        self.logger = get_logger(self.__class__.__name__)

    @classmethod
    def create_instance(cls, crawler):
        settings = crawler.settings
        mongo_params = settings.get('MONGODB_PARAMS', None)
        db_name = settings.get('MONGODB_DB', None)
        project_name = settings.get('PROJECT_NAME', None)

        conn = AsyncIOMotorClient(**mongo_params) if mongo_params else AsyncIOMotorClient()

        col = conn[db_name][project_name]
        o = cls(conn, col)
        crawler.subscriber.subscribe(o.spider_closed, event=spider_closed)
        return o

    async def process_item(self, item, spider):
        await self.col.insert_one(item.to_dict())
        return item

    async def spider_closed(self):
        self.logger.info('MongoDB closed.')
        self.conn.close()

