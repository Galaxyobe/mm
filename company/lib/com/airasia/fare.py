# -*- coding:UTF-8 -*-
"""
Airasia fare parse

This module provides parse Airsaia fare with BeautifulSoup4.

Usage:
    fareParse = AirasiaFareParse()
    fareParse.set_html('xxx.html')
    fare = fareParse.get_fare()
"""

import re

from bs4 import BeautifulSoup


class AirasiaFareParse(object):

    """
    AirasiaFareParse class
    """

    def __init__(self, doc=None):
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
            string: a prettify string
        """

        return self.soup.prettify()

    def __get_price(self, price):
        """
        Use regular get the number price

        Give a string to get the price

        Args:
            @param price: a format as 000.00 string

        Returns:
            string: a price string
            or
            None
        """
        price = re.findall(r'(\d*\.\d*)', price.replace(',', ''))[0]

        return float(price) if price else -1.0

    def get_fare(self):
        """
        Get the parse fare

        Parse data and return

        Args:
            None

        Returns:
            dict: a dict such as
                    {
                        'Advance Passenger Processing Service (E7)': '12.00',
                        'Children': '1196.00',
                        'Adult(s)': '1286.00',
                        'International Arrival and Departure Fees (Thailand)': '6.00',
                        'Fares': '2744.00',
                        'Total': '2852.00',
                        'Infant(s)': '370.00',
                        'Airport Tax': '90.00'
                    } or {}
        """

        fare = {}
        # section-total-display-price
        total_price = self.soup.find('div',
                                     class_='section-total-display-price')
        if total_price:
            fare['Total'] = self.__get_price(
                total_price.select('span')[0].string)

        infos = self.soup.find_all('div',
                                   class_='price-display-summary-line-item')

        for info in infos:

            name = info.select('div.pull-left')
            cost = info.select('div.pull-right')

            if name and cost:
                name = name[0].string
                cost = cost[0].string
                fare[name] = self.__get_price(cost)

        return fare


if __name__ == '__main__':

    fareParse = AirasiaFareParse(
        open('./html/fare-1.html'))
    fare = fareParse.get_fare()

    print fare
