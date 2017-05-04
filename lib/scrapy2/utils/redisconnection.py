# -*- coding: utf-8 -*-

import redis

REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}

# Shortcut maps 'setting name' -> 'parmater name'.
REDIS_PARAMS_MAP = {
    'REDIS_HOST': 'host',
    'REDIS_PORT': 'port',
    'REDIS_DB': 'db',
    'REDIS_PASSWORD': 'password',
}


def get_redis_from_settings(settings):
    """Returns a redis client instance from given Scrapy settings object.

    This function uses ``get_client`` to instantiate the client and uses
    ``defaults.REDIS_PARAMS`` global as defaults values for the parameters. You
    can override them using the ``REDIS_PARAMS`` setting.

    Parameters
    ----------
    settings : Settings
        A scrapy settings object. See the supported settings below.

    Returns
    -------
    server
        redis client instance.

    Other Parameters
    ----------------
    REDIS_HOST : str, optional
        Server host.
    REDIS_PORT : int, optional
        Server port.
    REDIS_DB : int, optional
        db.

    """
    params = REDIS_PARAMS.copy()
    p = settings.getdict('REDIS_PARAMS')
    for source, dest in REDIS_PARAMS_MAP.items():
        val = p.get(source)
        if val:
            params[dest] = val
    return redis.ConnectionPool(**params)


# Backwards compatible alias.
from_settings = get_redis_from_settings
