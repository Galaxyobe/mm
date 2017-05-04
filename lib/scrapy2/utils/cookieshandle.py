# -*- coding:UTF-8 -*-

"""
Scrapy cookies handle

"""


def cookies_to_dict(headers_cookies):
    """
    Handle the headers cookies
    with headers headers cookies handle to scrapy support cookies

    Args:
        @param headers_cookies: the response headers cookies

    Returns:
        dict: a cookies dict
    """

    cookies = {}
    for i in headers_cookies:
        for item in i.split(';'):
            if item.find('=') != -1:
                value = item.split('=')
                cookies[value[0]] = value[1]

    return cookies
