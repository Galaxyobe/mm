# -*- coding: utf-8 -*-
"""
Redis backends
"""

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
# Define your item pipelines here
#
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from twisted.internet.threads import deferToThread

REDIS_PARAMS_DEFAULT = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
}


class Redis(object):
    """
    Redis class
    """

    def __init__(self, pool, pipeline):
        self.pool = pool
        self.pipeline = pipeline

    @classmethod
    def from_settings(cls, settings):
        """
        获得redis连接池
        """
        pool = None
        pipeline = None

        try:
            if settings.get('REDIS_PIPELINE'):
                pipeline = load_object(settings['REDIS_PIPELINE'])
            else:
                raise NotConfigured
            if settings.getdict("REDIS_BACKEND_PARAMS", REDIS_PARAMS_DEFAULT):
                param = settings.getdict("REDIS_BACKEND_PARAMS")
                pool = redis.ConnectionPool(**param)

        except Exception as ex:
            print '%s \nException:%s' % (__file__, ex)

        return cls(pool, pipeline)

    @classmethod
    def from_crawler(cls, crawler):
        """
        连接signals:engine_stopped
        """
        o = cls.from_settings(crawler.settings)
        crawler.signals.connect(o.engine_stopped,
                                signal=signals.engine_stopped)
        return o

    def engine_stopped(self):
        """
        爬虫引擎关闭时断开redis连接池
        """
        self.pool.disconnect()

    def process_item(self, item, spider):
        """
        处理item数据
        """
        try:
            server = redis.Redis(connection_pool=self.pool)
            return deferToThread(self.pipeline, server, item, spider)
        except Exception as ex:
            print '%s process_item \nException:%s' % (__file__, ex)
        return item
