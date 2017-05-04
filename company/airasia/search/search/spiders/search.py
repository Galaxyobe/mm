# -*- coding:UTF-8 -*-
"""
Airasia Search Spider
"""
import json
import re
import time

from scrapy.utils.project import get_project_settings

from com.airasia.fare import AirasiaFareParse
from com.airasia.flight import AirasiaFlightParse
from com.utils.key import KeyGenerator
from scrapy2.spiders import RedisSpider
from scrapy2.utils.cookieshandle import cookies_to_dict


class AirasiaSearchSpider(RedisSpider):
    """
    AirasiaSearchSpider instance
    """
    domain = "airasia"
    name = "search"
    source = 'AKB2C'
    redis_key = '{domain}:{name}:queue'.format(domain=domain, name=name)

    allowed_domains = ["airasia.com"]

    def __init__(self, *args, **kwargs):
        super(AirasiaSearchSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.flightParse = AirasiaFlightParse()
        self.fareParse = AirasiaFareParse()
        self.keyGenerator = KeyGenerator()
        self.use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', False)
        self.is_zset = self.settings.getbool('REDIS_START_URLS_IS_ZSET', False)
        self.redis_key_live = self.settings.getint('REDIS_KEY_LIVE_TIME',
                                                   300)

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
        if url.find('Flight/Select?') > 0:
            return True
        return False

    def parse(self, response):

        try:
            filename = 'download/flight/%s.html' % response.url.split("/")[-1]
            with open(filename, 'wb') as _file:
                _file.write(response.body)
        except:
            pass

        # Cookies处理
        cookies = None

        for key, value in response.headers.items():
            if key == 'Set-Cookie':
                cookies = cookies_to_dict(value)

        # print cookies

        self.flightParse.set_html(response.body)
        rows = self.flightParse.get_rows()

        # TODO: 数据完整性

        for row in rows:
            schedule = self.flightParse.get_schedule(row)
            itinerary = self.flightParse.get_itinerary(row)

            Flights = {}
            flight = {}

            routes = itinerary['route'].split('-')
            depart = routes[0]
            arrive = routes[-1]

            for key in itinerary.keys():

                if key.find('Flight') > -1:
                    # 获取航班
                    Flights[key] = itinerary[key]
                    index = int(re.findall(r'\d', key)[0]) - 1
                    flight[index] = {}
                    flight[index]['date'] = itinerary[key]['date']
                    flight[index]['no'] = itinerary[key]['no']

            no = '/'.join([value['no'] for key, value in flight.items()])
            date = flight[0]['date']

            key = self.keyGenerator.generator_detail_key(depart=depart,
                                                         arrive=arrive,
                                                         source=self.source,
                                                         no=no,
                                                         date=date)

            fare_redis_key = '{domain}:{name}:queue'.format(domain=self.domain,
                                                            name='fare')
            save_one = self.server.sadd if self.use_set else self.server.rpush
            # 获取舱位及其费用链接
            if 'tag' in itinerary.keys():
                for cabin, value in itinerary['tag'].items():
                    # print cabin, value['remaining'], value['url']
                    # 把URL放入fare的调度队列中
                    if self.is_zset:
                        self.server.zadd(fare_redis_key,
                                         100.0,
                                         value['url'])
                    else:
                        save_one(fare_redis_key, value['url'])
                    # 编码URL作为redis的hash键，用于给其他的爬虫传递数据

                    url_key = self.keyGenerator.generator_data_key(
                        value['url'])
                    meta = json.dumps({'key': key, 'class': cabin})

                    data = {'meta': meta,
                            'cookies': cookies,
                            'priority': 100,
                            'expire': int(time.time() + 24 * 60 * 60)}
                    self.server.hmset(url_key, data)
                    self.server.expire(url_key, 24 * 60 * 60)

            update = time.strftime('%Y-%m-%d %H:%M:%S',
                                   time.localtime(time.time()))
            # 返回数据到存储后端
            yield {
                # 'id': 'flight',                   # 标示此次yield
                'key': key,
                'depart': depart,
                'arrive': arrive,
                'date': date,
                'schedule': schedule,           # 时刻表
                'no': no,                       # 所有航班号用/分隔
                'type': itinerary['type'],      # 类型：Fly-Through/Direct
                'route': itinerary['route'],    # 行程摘要 CNX-(KUL)-PEK
                'source': self.domain,          # 数据来源
                'flights': Flights,             # 所有航班信息
                'flight_update': update,        # 更新时间
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
