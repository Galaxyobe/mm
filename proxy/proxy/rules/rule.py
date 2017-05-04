# -*- coding: utf-8 -*-
"""
爬虫规则
"""


class ProxyRules(object):
    """
    爬虫规则类
    """

    def __init__(self):
        pass

    Rules = {
        'rule1': {
            # name: 名称 字段名称不可改变保持唯一
            'name': 'xicidaili',
            # enable: 使能标志 字段名称不可改变
            'enable': True,
            # domains: 域名 字段名称不可改变 多域名用逗号分隔
            'domains': 'xicidaili.com',
            # start_urls: 起始URL 字段名称不可改变 多域名用逗号分隔
            'start_urls': 'http://www.xicidaili.com/nn/',
            # selector: 选择器 解析方式 ['xpath','css']  字段名称不可改变
            'selector': 'xpath',
            # datas: [list] 数据 字段名称不可改变
            # datas中的fields里的字段会组成一个dict返回数据 TODO
            'datas': [
                {
                    # name: 数据名称 字段名称不可改变
                    'name': 'iplist',
                    # type: field的数据来源类型 ['table','string'] 字段名称不可改变
                    'type': 'table',
                    # table.trs: 表格的tr 字段名称不可改变 当type=table时 该属性有效
                    'table.trs': '//*[@id="ip_list"]//tr[(@class)]',
                    # fields: 字段 字段名称不可改变  可自定义数据字段 不可重复
                    'fields': {
                        # ip地址
                        'ip': 'td[2]/text()',
                        # 端口
                        'port': 'td[3]/text()',
                        # 匿名状态:高匿,匿名,透明
                        'anonymousp': 'td[5]/text()',
                        # 连接协议类型:HTTP,HTTPS
                        'protocol': 'td[6]/text()',
                    },
                },
            ],
            # pages: 页面 字段名称不可改变
            'pages': {
                # total: [int] 页面总数 字段名称不可改变
                'total': '//*[@id="body"]/div[2]/a[10]/text()',
                # generator: 页面生成器 字段名称不可改变
                'generator': 'http://www.xicidaili.com/nn/%s',
                # max: 允许最大的页数 字段名称不可改变 0 - 不使能
                'max': 1,
            },
        },
    }
