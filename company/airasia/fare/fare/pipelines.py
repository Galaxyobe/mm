# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class AirasiaFarePipeline(object):
    def process_item(self, item, spider):
        print item
        return item


def AirasiaFareRedisPipeline(server, item, spider):
    """
    AirasiaFareRedisPipeline
    Redis backend
    """
    try:
        server.hmset(item['key'], item)
        server.expire(item['key'], spider.redis_key_live)
        spider.logger.info('add %s to hash:%s' % (item, item['key']))
    except Exception as ex:
        spider.logger.error('%s process_item \nException:%s' % (__file__, ex))
