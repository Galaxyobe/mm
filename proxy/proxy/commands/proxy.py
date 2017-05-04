# -*- coding: utf-8 -*-
"""
scrapy自定义命令
"""
import logging

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ..rules.rule import ProxyRules
from ..spiders.common import CommonSpider


class ProxyCommand(ScrapyCommand):
    """
    ProxyCommand class
    """
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    logger = logging.getLogger(__name__)

    def short_desc(self):
        return '根据规则运行爬虫'

    def run(self, args, opts):
        """
        根据项目设置实例化处理进程
        """
        # 获取通用项目设置
        process = CrawlerProcess(get_project_settings())
        # 根据规则启动爬虫
        proxyRules = ProxyRules()
        for (k, v) in proxyRules.Rules.iteritems():
            if isinstance(v, dict):
                if 'enable' in v and v['enable']:
                    self.logger.info('Start spider name:%(name)s rule:%(rule)s',
                                     {'name': v['name'], 'rule': k})
                    process.crawl(CommonSpider, v)

        # the script will block here until the crawling is finished
        process.start()
