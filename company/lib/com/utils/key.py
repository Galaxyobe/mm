# -*- coding:UTF-8 -*-
"""
Generator the flight key to

This module provides generator some key

Usage:

"""
import hashlib


class KeyGenerator(object):
    """
    KeyGenerator class
    """

    def __init__(self):
        pass

    def md5(self, *args):
        """
        Generator md5

        with hashlib generator md5

        Args:
            *args:arg list
        Returns:
            string:md5
        """
        md5 = hashlib.md5()
        for arg in args:
            if not isinstance(arg, str):
                arg = str(arg)
            md5.update(arg)
        return md5.hexdigest()

    def generator_flight_key(self, depart, arrive, source, no, date):
        """
        Generator flight key

        use hashlib md5 the params

        Args:
            @param depart:
            @param arrive:
            @param source: data from
            @param no: all flight no in this route
            @param date:
        Returns:
            string: md5
        """

        date = date.replace('-', '')
        no = no.replace(' ', '')
        no = (self.md5(no)[8:-8])

        key = '{depart}{arrive}{source}{no}{date}'.format(
            depart=depart,
            arrive=arrive,
            source=source,
            no=no,
            date=date)

        return key

    def generator_set_key(self, depart, arrive, date):
        """
        生成一个集合键

        集合键里是数据的详情键

        参数:
            @param depart:
            @param arrive:
            @param date:
        返回:
            string:
        """
        date = date.replace('-', '')
        key_str = '{depart}:{arrive}:{date}'
        key = key_str.format(date=date,
                             depart=depart,
                             arrive=arrive)

        return key

    def generator_detail_key(self, depart, arrive, date, source, no):
        """
        生成一个详情键

        详情键里是数据的明细，其键存放在集合键中

        参数:
            @param depart:
            @param arrive:
            @param source: data from
            @param no: all flight no in this route
            @param date:
        Returns:
            string: md5
        """
        date = date.replace('-', '')
        no = no.replace(' ', '')
        key_str = '{depart}:{arrive}:{date}:{source}:{no}'
        key = key_str.format(date=date,
                             depart=depart,
                             arrive=arrive,
                             source=source,
                             no=self.md5(no)[8:-8])

        return key

    def generator_data_key(self, url):
        """
        生成一个附加数据键

        爬虫在抓取url时会以该键读取附加的数据
        附加的数据可以是cookie，meta等

        参数:
            @param url: url
        返回:
            string:
        """

        key = 'D:{md5}'.format(md5=self.md5(url))

        return key


if __name__ == '__main__':

    keyGenerator = KeyGenerator()
    print keyGenerator.generator_flight_key(depart='PEK',
                                            arrive='CNX',
                                            source='AKB2C',
                                            no='AK855/D7312',
                                            date='2017-04-06')
