# -*- coding:UTF-8 -*-
"""
Airasia Fare Spider
"""
import json
import time

import scrapy
from scrapy.utils.project import get_project_settings

from com.airasia.fare import AirasiaFareParse
from com.utils.key import KeyGenerator
from scrapy2.spiders import RedisSpider


class AirasiaFareSpider(RedisSpider):
    """
    AirasiaFareSpider instance
    """
    domain = "airasia"
    name = "fare"
    source = 'AKB2C'
    redis_key = '{domain}:{name}:queue'.format(domain=domain, name=name)

    allowed_domains = ["airasia.com"]

    def __init__(self, *args, **kwargs):
        super(AirasiaFareSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.fareParse = AirasiaFareParse()
        self.keyGenerator = KeyGenerator()
        self.use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', False)
        self.is_zset = self.settings.getbool('REDIS_START_URLS_IS_ZSET', False)
        self.redis_key_live = self.settings.getint('REDIS_KEY_LIVE_TIME',
                                                   300)

    def make_requests_from_url(self, url):
        """
        重写make_requests_from_url

        根据URL的编码从redis中取出数据加到Request中

        参数:
            @param url:
            @param priority: 优先级
        返回:
            Request对象
        """

        if url.find('SellKeys') == -1:
            return

        url_key = self.keyGenerator.generator_data_key(url)
        data = self.server.hgetall(url_key)
        if not data:
            self.logger.debug('no key:%s data,url:%s' % (url_key, url))
            return
        cookies = eval(data['cookies'])
        meta = json.loads(data['meta'])
        # print '-' * 80
        # print cookies
        # print '-' * 80
        return scrapy.Request(url, cookies=cookies, meta=meta)

    def rescheduler_url_regex(self, url):
        """
        判断url是否有效
        无效的url不参与重新调度
        reschedulertimer.py文件调用
        参数:
            @param url: 判断的url
        返回:
            bool: True-有效 False-无效
        """
        if url.find('Flight/PriceItinerary?') > 0:
            return True
        return False

    def parse(self, response):
        """
        Parse the flight fare
        """

        try:
            filename = 'download/fare/%s.html' % response.url.split("=")[-1]
            with open(filename, 'wb') as _file:
                _file.write(response.body)
        except:
            pass

        self.fareParse.set_html(response.body)
        # print self.fareParse.prettify()
        fare = self.fareParse.get_fare()

        # 数据为空处理
        if not fare:
            # cookie不可用删除
            url_key = self.keyGenerator.generator_data_key(response.url)
            self.server.delete(url_key)
            return

        # 类型
        _type = 0

        for key in fare:
            # 成人
            if 'Adult(s)' in key:
                _type += 1
            # 儿童
            elif 'Children' in key:
                _type += 2
            # 婴儿
            elif 'Infant(s)' in key:
                _type += 4

        # print fare
        key = response.meta['key']
        cabin = response.meta['class']

        update = time.strftime('%Y-%m-%d %H:%M:%S',
                               time.localtime(time.time()))
        yield {
            # 'id': 'fare',           # 标示此次yield
            'key': key,
            # 'class': cabin,         # 舱位等级
            # 类型 1:成人/3:成人+儿童/5:成人+婴儿/7:成人+儿童+婴儿
            'class:%s:%s' % (cabin, _type): fare,
            'fare_update': update,        # 更新时间
        }

    def downloader_exception_handle(self, request, reason, spider):
        """
        DOWNLOADER_MIDDLEWARES:DownloaderExceptionHandle
        downloader exception handle func
        """
        # spider.save('%s' % 'AirAsiaSearch:failed', request.url)
        spider.logger.error("%(request)s \nException: %(reason)s",
                            {'request': request,
                             'reason': reason})
