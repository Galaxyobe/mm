# -*- coding: utf-8 -*-
import time
from threading import Timer

from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from scrapy.utils.response import response_status_message
from twisted.internet import defer
from twisted.internet.error import (ConnectError, ConnectionDone,
                                    ConnectionLost, ConnectionRefusedError,
                                    DNSLookupError, TCPTimedOutError,
                                    TimeoutError)
from twisted.web.client import ResponseFailed
from w3lib.url import safe_url_string

from company.utils.key import KeyGenerator
from six.moves.urllib.parse import urljoin


class ReschedulerTimer(object):

    """
    Scrapy crawl rescheduler timer

    ----------
        RESCHEDULER_ENABLED default:True
                True: enable extension
                False: disabled it
        RESCHEDULER_INTERVAL must
                None or not defined it to disabled it
                float number interval recall
        RESCHEDULER_DOWNEXCEPTION_POLICY default:Retry
                下载异常处理策略:Retry/Delete 重试/删除
    """
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_HANDLE = (defer.TimeoutError, TimeoutError, DNSLookupError,
                            ConnectionRefusedError, ConnectionDone,
                            ConnectError, ConnectionLost, TCPTimedOutError,
                            ResponseFailed, IOError, TunnelError)

    def __init__(self, crawler):
        self.crawler = crawler
        self.interval = crawler.settings.getfloat('RESCHEDULER_INTERVAL')
        self.retry = crawler.settings.getbool('RETRY_ENABLED')
        self.max_retry_times = crawler.settings.getint('RETRY_TIMES')
        self.policy = crawler.settings.get('RESCHEDULER_DOWNEXCEPTION_POLICY',
                                           'Retry')

        if not self.interval:
            raise NotConfigured

        self.keyGenerator = KeyGenerator()

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('RESCHEDULER_ENABLED', True):
            raise NotConfigured
        return cls(crawler)

    def process_request(self, request, spider):
        """
        Request处理
        """
        request.meta['LATEST_SCHEDULER_TIMESTAMP'] = time.time()

    def process_response(self, request, response, spider):
        """
        Response处理
        """

        # 打印出状态码不是200的url
        allowed_status = [200]
        if response.status not in allowed_status:
            spider.logger.info('%(request)s status: %(status)s',
                               {'status': response.status, 'request': request})
        # url匹配规则
        if 'spider.rescheduler_url_regex' in dir():
            if hasattr(spider.rescheduler_url_regex, '__call__'):
                if not spider.rescheduler_url_regex(request.url):
                    spider.logger.info('%s is not expect' % request.url)
                    return response

        # 处理重定向
        allowed_3xx_status = (301, 302, 303, 307)
        if 'Location' in response.headers or response.status in allowed_3xx_status:
            location = safe_url_string(response.headers['location'])
            redirected_url = urljoin(request.url, location)
            spider.logger.info('redirecte url: %(redirected)s from %(request)s',
                               {'redirected': redirected_url, 'request': request})

        priority = 1

        timestamp = request.meta.get('LATEST_SCHEDULER_TIMESTAMP',
                                     time.time())
        delta = time.time() - timestamp

        if delta > self.interval:
            self.__save_to_redis(spider, request.url, priority)
        else:
            Timer(self.interval - delta,
                  self.__save_to_redis,
                  (spider, request.url, priority)).start()

        return response

    def process_exception(self, request, exception, spider):
        """
        下载异常处理
        """
        if isinstance(exception, self.EXCEPTIONS_TO_HANDLE):
            return self.__handle(request, spider)

    def __handle(self, request, spider):
        priority = -1
        if self.retry:
            retries = request.meta.get('retry_times', 0) + 1
            if retries > self.max_retry_times:
                Timer(self.interval,
                      self.__save_to_redis,
                      (spider, request.url, priority)).start()
        else:
            Timer(self.interval,
                  self.__save_to_redis,
                  (spider, request.url, priority)).start()

    def __save_to_redis(self, spider, url, priority):

        url_key = self.keyGenerator.generator_data_key(url)

        if self.policy == 'Delete':
            spider.server.delete(url_key)
            return

        data = spider.server.hgetall(url_key)
        expire = int(data.get('expire', -1))  # 过期时间戳

        # 没有设置过期时间戳，默认不重新调度
        if expire < 0:
            return
        # URL 已过期
        if time.time() > expire:
            return

        # 优先级
        _priority = float(data.get('priority', 100)) + priority

        spider.logger.debug('add url: %s into %s <%d>' %
                            (url, spider.redis_key, _priority))
        # URL 有效
        spider.server.hset(url_key, 'priority', _priority)

        if spider.is_zset:
            spider.server.zadd(spider.redis_key,
                               _priority,
                               url)
        else:
            save_one = spider.server.sadd if spider.use_set else spider.server.rpush
            save_one(spider.redis_key, url)
