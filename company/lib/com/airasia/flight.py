# -*- coding:UTF-8 -*-
"""
Airasia flight parse

This module provides parse Airsaia flight with BeautifulSoup4.

Usage:
    flightParse = AirasiaFlightParse()
    flightParse.set_html('xxx.html')
    rows = self.flightParse.get_rows()
    for row in rows:
        info = {}
        info['schedule'] = self.flightParse.get_schedule(row)
        info['stops'] = self.flightParse.get_stops(row)
        info['itinerary'] = self.flightParse.get_itinerary(row)
        infos.append(info)
        for type, value in info['itinerary'].items():
            for k, v in value.items():
                if 'url' == k:
                    yield scrapy.Request(url=v,
                                        meta={'type': k},
                                        callback=self.parse_fare,
                                        cookies=cookies)
"""

import json
import re
import urllib
import urlparse

from bs4 import BeautifulSoup

from com.utils.tools import deep_combine


class AirasiaFlightParse(object):
    """
    AirasiaFlightParse class
    """

    __fare_query_url = 'https://booking.airasia.com/Flight/PriceItinerary?\
SellKeys%5B%5D=2~C~~C01H00~AAX1~~140~X%5E1~A~~A01H00H~AAB1~~46~%7CD7~+317~+\
~~PEK~04%2F28%2F2017+02%3A15~KUL~04%2F28%2F2017+08%3A25~%5EAK~+856~+\
~~KUL~04%2F28%2F2017+14%3A45~CNX~04%2F28%2F2017+16%3A25~&\
MarketValueBundles%5B%5D=false&MarketProductClass%5B%5D=PM\
&MarketUpgradePrice%5B%5D=2188.0000000&SaveMarketBundlesSession=true&\
instart_disable_injection=true'

    __fare_query = {
        'SellKeys[]': '',
        'MarketValueBundles[]': 'false',
        'MarketProductClass[]': '',
        'MarketUpgradePrice[]': 0,
        'SaveMarketBundlesSession': 'true',
        'instart_disable_injection': 'true',
    }

    def __init__(self, doc=None):
        self.__fare_query_url_parse = urlparse.urlparse(self.__fare_query_url)
        if doc:
            self.set_html(doc)

    def set_html(self, doc):
        """
        Set html doc for parser

        Give a html doc to parser the data

        Args:
            @param doc: html doc

        Returns:
            None
        """
        self.soup = BeautifulSoup(doc, 'lxml')

    def prettify(self):
        """
        Prettify the html doc

        return a prettify html

        Args:
            None

        Returns:
            string:a prettify string
        """

        return self.soup.prettify()

    def get_schedule(self, row):
        """
        Get the flight's schedule,this airport and time

        Give a flight row info in html to parse the airport and time
            Depart		 Arrive
            02:15        08:25
            (PEK)        (KUL)
        Args:
            @param row: a flight row in html from BeautifulSoup4 tag

        Returns:
            list: such as
                [(u'PEK', u'05:40'),
                 (u'KUL', u'11:50'),
                 (u'KUL', u'14:45'),
                 (u'CNX', u'16:25')]
                or []
        """

        schedule = []
        # 从航班中获取时刻表
        infos = row.find_all('tr',
                             class_=re.compile(r'fare-\w*-row'))
        for info in infos:
            # print info.prettify()
            # 选出时刻表
            details = info.find_all('td', class_='avail-table-detail')
            for detail in details:
                # print detail.prettify()
                # 获取出发/抵达时间
                time = detail.select('div > div.avail-table-bold')[0].string
                # 获取出发/抵达机场
                airport = detail.select('div > div:nth-of-type(2)')[0].string

                airport = re.findall(
                    ur"(?<=[\(])[^\)]+(?=[\)])", airport)[0]

                schedule.append((airport, time))

        return schedule

    def get_stops(self, row):
        """
        Get the flight stops string

        Give a flight row info in html to parse

        Args:
            @param flight: a flight row in html from BeautifulSoup4 tag

        Returns:
            list:such as ['Layover'] or [u'经停'] or [] if not exist
        """
        stops = []
        # 查看是否有中途停留信息
        infos = row.find_all('div', class_='avail-stops')
        for info in infos:
            stops.append(info.string)
            # print info.string
        return stops

    def get_itinerary(self, row):
        """
        Get the flight itinerary

        Give a flight row info in html to parse
        get the fare's click info to request the fare html

        Args:
            @param flight: a flight row in html from BeautifulSoup4 tag

        Returns:
            dict:such as
                        {
                            'route': u'CNX-(KUL)-PEK',
                            'type': u'Fly-Through',
                            'Flight 1': {
                                'depart': u'CNX',
                                'no': u'AK855',
                                'brand': u'AK',
                                'date': u'2017-07-12',
                                'arrive': u'KUL',
                                'tag': {
                                    'EP': {
                                        'kid_price': 1063.0,
                                        'adult_price': 1063.0
                                    },
                                    'PM': {
                                        'kid_price': 907.0,
                                        'adult_price': 907.0
                                    }
                                }
                            },
                            'Flight 2': {
                                'depart': u'KUL',
                                'no': u'D7312',
                                'brand': u'D7',
                                'date': u'2017-07-12',
                                'arrive': u'PEK',
                                'tag': {
                                    'EP': {
                                        'kid_price': 0.0,
                                        'adult_price': 0.0
                                    },
                                    'PM': {
                                        'kid_price': 1598.0,
                                        'adult_price': 1598.0
                                    }
                                }
                            },
                            'tag': {
                                'EP': {
                                    'url': 'http://',
                                    'remaining': 9
                                },
                                'PM': {
                                    'url': 'http://',
                                    'remaining': 2
                                }
                            }
                        }
        """

        itinerary = {}
        # 获取所有航费信息
        infos = row.find_all('td', class_='avail-fare')

        for info in infos:
            # 获取要组成的链接信息
            # print info.prettify()
            radio = info.find('input')

            if radio:
                self.__fare_query['SellKeys[]'] = radio['value']
                self.__fare_query['MarketProductClass[]'] = radio[
                    'data-productclass']
                self.__fare_query['MarketUpgradePrice[]'] = radio[
                    'data-upgradeprice']

                detail = self.__parse_data_json(
                    radio['data-json'], radio['data-productclass'])

                query = self.urlencode(self.__fare_query)

                url = urlparse.urlunparse((self.__fare_query_url_parse.scheme,
                                           self.__fare_query_url_parse.netloc,
                                           self.__fare_query_url_parse.path,
                                           self.__fare_query_url_parse.params,
                                           query,
                                           self.__fare_query_url_parse.fragment))

                detail['tag'] = {}
                detail['tag'][radio['data-productclass']] = {}
                detail['tag'][radio['data-productclass']]['url'] = url
                # 获取剩余位置数量
                remaining = info.find(
                    'div', class_='avail-table-seats-remaining')
                remain = 9
                if remaining:
                    remain = re.sub(r"\D", "", remaining.string)

                detail['tag'][radio['data-productclass']]['remaining'] = remain
                itinerary[radio['data-productclass']] = detail

        return reduce(deep_combine, itinerary.values())

    def get_rows(self):
        """
        Get the flight rows

        Generator a flight row info in html from BeautifulSoup4
        the generator row use for parse details

        Args:
            None

        Returns:
            list: a generator list
        """

        # 获取所有航班
        rows = self.soup.find_all('tr', class_=re.compile(r'fare-\w*-row'))

        for row in rows:
            # 选出正确的航班
            if row.find('tr', class_=re.compile(r'fare-\w*-row')):
                yield row

    def __parse_data_json(self, sdata, cabin):
        """
        Parse the flight row data-json

        Parse a flight row data-json, get useful info

        Args:
            @param sdata: the data-json string
            @param cabin: the product class

        Returns:
            dict: a flight info such as
                    {
                        'route': u'PEK-(KUL)-CNX',
                        'type': u'Fly-Through',
                        'Flight 1': {
                            'depart': u'PEK',
                            'no': u'D7317',
                            'brand': u'D7',
                            'date': u'2017-05-31',
                            'arrive': u'KUL',
                            'tag': {
                                'EP': {
                                    'kid_price': 747.0,
                                    'adult_price': 837.0
                                }
                            }
                        },
                        'Flight 2': {
                            'depart': u'KUL',
                            'no': u'AK856',
                            'brand': u'AK',
                            'date': u'2017-05-31',
                            'arrive': u'CNX',
                            'tag': {
                                'EP': {
                                    'kid_price': 449.0,
                                    'adult_price': 449.0
                                }
                            }
                        }
                    }
        """
        data_json = json.loads(sdata)
        flights = {}

        for data in data_json:
            # 航线 dimension13:PEK-(KUL)-CNX
            flights['route'] = data['dimension13']
            # dimension15:Fly-Through,Direct
            flights['type'] = data['dimension15']

            flight = {}

            # 出发 dimension2:PEK
            flight['depart'] = data['dimension2']
            # 抵达 dimension3:KUL
            flight['arrive'] = data['dimension3']
            # 日期 dimension5:2017-05-31
            flight['date'] = data['dimension5']
            # 航班编号 dimension16:D7317
            flight['no'] = data['dimension16']
            # 机场 brand:D7
            flight['brand'] = data['brand']
            # 价格 price:
            if data['dimension6'] not in flights:
                flight['tag'] = {}
                flight['tag'][cabin] = {}
            else:
                flight['tag'] = flights[data['dimension6']]['tag']

            if data['variant'] == 'Adults':
                flight['tag'][cabin]['adult_price'] = float(
                    data['price'])
            elif data['variant'] == 'Kids':
                flight['tag'][cabin]['kid_price'] = float(
                    data['price'])

            # dimension6:Flight 1,Flight 2
            if data['dimension6'] not in flights:
                flights[data['dimension6']] = flight
            else:
                flights[data['dimension6']].update(flight)

        return flights

    def urlencode(self, query):
        """
        Encode query for url

        Give a query to encode specail a url query

        Args:
            @param query: a query want to encode the string

        Returns:
            string: a encode query string
        """
        lst = []
        for key, value in query.items():
            key = urllib.quote_plus(str(key))
            if isinstance(value, str):
                value = urllib.quote_plus(value, '~')
                lst.append(key + '=' + value)

        return '&'.join(lst)


if __name__ == '__main__':

    from pprint import pprint

    flightParse = AirasiaFlightParse(
        open('./html/search-1.html'))

    # print flightParse.prettify()
    _rows = flightParse.get_rows()

    for _row in _rows:
        print 'schedule:%s' % flightParse.get_schedule(_row)
        print 'stops:%s' % flightParse.get_stops(_row)
        pprint('itinerary:%s' % flightParse.get_itinerary(_row))
        print '-' * 150
        itinerary = flightParse.get_itinerary(_row)
        for key in itinerary.keys():
            if 'tag' in key:
                for cabin, value in itinerary['tag'].items():
                    print cabin, value['remaining'], value['url']
