# -*- coding: utf-8 -*-
"""
运行爬虫
"""
import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ..rules.rule import ProxyRules
from ..spiders.common import CommonSpider

logger = logging.getLogger(__name__)


class RunCrawler(object):
    """
    RunCrawler class
    """

    def __init__(self):
        self.running = False
        self.process = None

    def start(self):
        """
        开始
        """
        if self.running:
            return
        self.running = True
        # 获取通用项目设置
        self.process = CrawlerProcess(get_project_settings())
        # 根据规则启动爬虫
        proxyRules = ProxyRules()
        for (k, v) in proxyRules.Rules.iteritems():
            if isinstance(v, dict):
                if 'enable' in v and v['enable']:
                    logger.info('Start crawl name:%(name)s rule:%(rule)s',
                                {'name': v['name'], 'rule': k})
                    self.process.crawl(CommonSpider, v)

        # the script will block here until the crawling is finished
        self.process.start()
        self.process.join()
        self.process.stop()
        self.running = False

    def stop(self):
        """
        停止
        """
        if self.running:
            self.running = False
            self.process.stop()
