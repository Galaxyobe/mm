# -*- coding:UTF-8 -*-
"""
Airasia flight search

This module provides Generator Airsaia search url.

Usage:
    search = AirasiaSearch()
    urls = search.generate_urls(o1='PEK',
                                d1='CNX',
                                dd1='2017-04-28',
                                ADT=1,
                                CHD=1,
                                inl=1)
    for url, date in urls:
        print url, date
"""

import datetime
import urllib
import urlparse


class AirasiaSearch(object):
    """
    AirasiaSearch class
    """

    search_url = 'https://booking.airasia.com/Flight/Select?\
o1=PEK&d1=CNX&culture=en-GB&dd1=2017-04-28&ADT=1&CHD=2&inl=1&\
s=true&mon=true&cc=CNY&c=false'

    __search_query_default = {
        's': 'false',
        'mon': 'true',
        'cc': 'CNY',
    }

    def __init__(self):
        self.__search_url_parse = urlparse.urlparse(self.search_url)

    def __set_query(self, o1, d1, dd1,
                    dd2=None,
                    ADT=1,
                    CHD=1,
                    inl=1,
                    culture='en-GB'):
        """
        Set query with params

        with search_url params to set query

        Args:
            None

        Returns:
            list:a query list
        """

        query = self.__search_query_default.copy()
        query['o1'] = o1
        query['d1'] = d1
        query['dd1'] = dd1
        query['ADT'] = ADT
        query['CHD'] = CHD
        query['inl'] = inl
        query['culture'] = culture  # zh-CN,en-GB
        query['dd2'] = dd2

        return query

    def generate_urls(self, days=1, round=True, **kwargs):
        """
        Generator the urls with kwargs and days

        Args:
            @param days: how many days want to generator with the query
            @param round: make one-way to one-way and return-way on same date
            @param **kwargs: a dict with want to update

        Returns:
            string: a string url
        """

        query = self.__set_query(**kwargs)

        base = query['dd1']

        for day in range(days):
            dd0 = datetime.datetime.strptime(base, '%Y-%m-%d')
            dd1 = dd0 + datetime.timedelta(days=day)
            date = dd1.strftime('%Y-%m-%d')
            # 传入的参数为单程
            # 把单程拆分为同一天的单程和返程
            if 'dd2' not in kwargs.keys():
                query['dd1'] = date
                if round:
                    query['dd2'] = date
                    query['r'] = 'true'
            else:
                query['r'] = 'true'

            for k, v in query.items():
                if not v:
                    del query[k]

            url = urlparse.urlunparse((self.__search_url_parse.scheme,
                                       self.__search_url_parse.netloc,
                                       self.__search_url_parse.path,
                                       self.__search_url_parse.params,
                                       urllib.urlencode(query),
                                       self.__search_url_parse.fragment))

            yield url, date


if __name__ == '__main__':
    search = AirasiaSearch()
    urls = search.generate_urls(o1='PEK',
                                d1='CNX',
                                dd1='2017-04-28',
                                ADT=1,
                                CHD=1,
                                inl=1)
    for url, date in urls:
        print url, date

"""
en
"""
# 单程
# https://booking.airasia.com/Flight/Select
# ?o1=PEK
# &d1=KUL
# &dd1=2017-04-28
# &ADT=3
# &CHD=2
# &inl=1
# &s=false
# &mon=true
# &cc=CNY

# 回程
# https://booking.airasia.com/Flight/Select
# ?o1=PEK
# &d1=KUL
# &dd1=2017-04-28
# &dd2=2017-05-24
# &r=true
# &ADT=3
# &CHD=2
# &inl=1
# &s=false
# &mon=true
# &cc=CNY

"""
cn
"""
# 单程
# https://booking.airasia.com/Flight/Select
# ?o1=PEK
# &d1=KUL
# &dd1=2017-04-28
# &ADT=6
# &CHD=2
# &inl=1
# &s=false
# &mon=true
# &cc=CNY
# 回程
# https://booking.airasia.com/Flight/Select
# ?o1=PEK
# &d1=KUL
# &dd1=2017-04-28
# &dd2=2017-05-17
# &r=true
# &ADT=6
# &CHD=2
# &inl=1
# &s=false
# &mon=true
# &cc=CNY
