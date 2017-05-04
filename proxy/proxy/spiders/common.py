# -*- coding: utf-8 -*-
"""
通用规则处理爬虫
"""
from scrapy.spiders import CrawlSpider

# from scrapy.utils.project import get_project_settings


class CommonSpider(CrawlSpider):
    """
    CommonSpider class
    """

    name = "CommonSpider"
    once = False

    def __init__(self, rule, *args, **kwargs):
        self.rule = rule
        self.name = rule['name']
        self.allowed_domains = rule['domains'].split(",")
        self.start_urls = rule['start_urls'].split(",")
        super(CommonSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # 设置选择器
        selector = response.xpath
        if 'selector' in self.rule:
            if self.rule['selector'] == 'css':
                selector = response.css
            else:
                selector = response.xpath
        # 处理页数
        if 'pages' in self.rule and not self.once:
            # 下次不在执行
            self.once = True
            pages = self.rule['pages']
            total = int(selector(pages['total']).re_first(r'\d+'))
            self.logger.debug("pages total:%s" % total)
            if pages['max'] and total > pages['max']:
                total = pages['max']
            for n in range(2, total + 1):
                url = pages['generator'] % n
                self.logger.debug("pages url:%s" % url)
                yield self.make_requests_from_url(url)
        # 处理数据
        if 'datas' in self.rule:
            datas = self.rule['datas']

            # 取出数据段
            for data in datas:
                # 解析数据
                if 'type' in data:
                    # 字段提取
                    if data['type'] == 'table':
                        # 字段从table中提取
                        if 'table.trs' in data:
                            trs = selector(data['table.trs'])
                            fields = data['fields']
                            # table_values = []
                            for tr in trs:
                                # 根据fields解析字段
                                value = {}
                                for (k, v) in fields.iteritems():
                                    if 'selector' in self.rule:
                                        if self.rule['selector'] == 'css':
                                            value[k] = tr.css(
                                                v).extract_first()
                                        else:
                                            value[k] = tr.xpath(
                                                v).extract_first()
                                yield value
                        else:
                            self.logger.error(
                                "Rule have not 'table.trs' field")
                    elif data['type'] == 'string':
                        # Todo:字段从string中提取
                        pass
                    else:
                        self.logger.error("Unsupported data type:%s" %
                                          data['type'])
