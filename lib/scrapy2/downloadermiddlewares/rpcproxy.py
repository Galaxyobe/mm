# -*- coding: utf-8 -*-
"""
使用rpc来获取一个可以的代理
"""

from scrapy import signals
from scrapy.exceptions import NotConfigured

from org.utils.rpc import RPCClient
import random


class RPCProxyMiddleware(object):
    """
    Proxy Middleware With RPC
    '''
    RPC Proxy Configure
    '''
    # 使能RPCProxy中间下载件
    RPCPROXY_ENABLED = True

    # RPC端口配置
    RPC_PARAMS = {
        'ip': '127.0.0.1',
        'port': 4242,
    }

    # 可使用代理的最底分数 默认: 100
    USABLE_SCORE = 100

    # 使用代理的概率 默认: 70(0-100)
    # 0-不使用代理 70-70%的链接使用代理访问
    USABLE_PROBABILITY = 30
    """

    def __init__(self, settings):
        self.settings = settings
        self.rpc = None
        self.client = None
        self.score = settings.getint('USABLE_SCORE', 100)
        self.probability = settings.getint('USABLE_PROBABILITY', 70)
        if self.probability == 0:
            raise NotConfigured

    @classmethod
    def from_crawler(cls, crawler):
        """
        设置
        """
        if not crawler.settings.getbool('RPCPROXY_ENABLED', True):
            raise NotConfigured
        if not crawler.settings.get('RPC_PARAMS'):
            raise NotConfigured
        ext = cls(crawler.settings)
        crawler.signals.connect(
            ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(
            ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        """
        打开
        """
        param = self.settings.get('RPC_PARAMS')
        self.rpc = RPCClient(**param)
        self.client = self.rpc.getClient()
        spider.logger.info("rpc client connected: %s", param)

    def spider_closed(self, spider):
        """
        关闭
        """
        self.rpc.close()
        spider.logger.info("rpc client closed")

    def process_request(self, request, spider):
        """
        请求
        获取并使用一个代理
        """
        # 使用随机数来决定是否使用代理
        rand = random.randint(1, 100)
        if rand > self.probability:
            return
        # 获取一个可以分数的代理
        data = self.client.get(self.score, protocol=['http', 'https'])
        if not data:
            return
        # 组装代理格式
        protocol = data['protocol'].lower()
        proxy = '{protocol}://{host}:{port}'.format(protocol=protocol,
                                                    host=data['ip'],
                                                    port=data['port'])

        spider.logger.debug('%s proxy %s', request, proxy)
        request.meta['proxy'] = proxy
