# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from com.utils.key import KeyGenerator

keyGenerator = KeyGenerator()


class AirasiaSearchPipeline(object):
    """
    AirasiaSearchPipeline
    """

    def process_item(self, item, spider):
        """
        process_item
        """
        return item


def AirasiaSearchRedisPipeline(server, item, spider):
    """
    AirasiaSearchRedisPipeline
    Redis backend
    """
    try:

        key = keyGenerator.generator_set_key(date=item['date'],
                                             depart=item['depart'],
                                             arrive=item['arrive'])
        server.sadd(key, item['key'])
        server.hmset(item['key'], item)
        server.expire(item['key'], spider.redis_key_live)
        spider.logger.info('add %s to sort:%s' % (item['key'], key))
        spider.logger.info('add %s to hash:%s' % (item, item['key']))
    except Exception as ex:
        spider.logger.error('%s process_item \nException:%s' % (__file__, ex))
