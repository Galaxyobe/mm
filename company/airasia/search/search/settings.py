# -*- coding: utf-8 -*-

# Scrapy settings for airasia project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'search'

SPIDER_MODULES = ['search.spiders']
NEWSPIDER_MODULE = 'search.spiders'


""" Scrapy_redis Configure """

# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy2.core.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_ENABLED = False

DUPEFILTER_CLASS = "scrapy2.dupefilters.redisdupefilters.RFPDupeFilter"

# DUPEFILTER_CLASS = "scrapy2.dupefilters.redisbloomdupefilters.ReidsBloomDupeFilter"

SCHEDULER_DUPEFILTER_KEY = 'airasia:search:dupefilter'

SCHEDULER_QUEUE_KEY = 'airasia:search:requests'

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# Specify the host and port to use when connecting to Redis (optional).
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': 'datacenter.io',
}

REDIS_START_URLS_AS_SET = True
REDIS_START_URLS_IS_ZSET = True
REDIS_ITEM_AS_SET = True


""" Log Configure """
# Configure log level
# See http://scrapy.readthedocs.io/en/latest/topics/logging.html#logging-settings
# See
# http://scrapy.readthedocs.io/en/latest/topics/settings.html#std:setting-LOG_ENABLED
LOG_LEVEL = 'INFO'
# See http://scrapy.readthedocs.io/en/latest/topics/settings.html#log-file
# LOG_FILE = 'log/%s %s.log' % (BOT_NAME, time.strftime('%Y-%m-%d %H:%M:%S'))
# See http://scrapy.readthedocs.io/en/latest/topics/settings.html#log-stdout
# LOG_STDOUT = False


REDIRECT_ENABLED = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN=16
# CONCURRENT_REQUESTS_PER_IP=16

# Configure download timeout  (default: 180)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-timeout
# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 180

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False
TELNETCONSOLE_PORT = [16023, 16032]

""" ReschedulerTime Configure """

RESCHEDULER_ENABLED = True
RESCHEDULER_INTERVAL = 60


""" DownloadStats Configure """
# Configure DownloadStats extension

DOWNLOADSTATS_ENABLED = True
DOWNLOADSTATS_INTERVAL = 60
DOWNLOADREQUEST_DISPLAY = True


""" Redis Backend Configure """
# Configure redisbackend
REDIS_BACKEND_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'password': 'datacenter.io',
}

REDIS_PIPELINE = 'search.pipelines.AirasiaSearchRedisPipeline'
# redis hash key
REDIS_KEY_LIVE_TIME = 300


# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
#     'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
#     'Connection': 'keep-alive',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'airasia.middlewares.MyCustomSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy2.downloadermiddlewares.rotateuseragent.RotateUserAgentMiddleware': 400,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 700,
    'scrapy2.downloadermiddlewares.exceptionhandle.DownloaderExceptionHandle': 950,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy2.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy2.downloadermiddlewares.reschedulertimer.ReschedulerTimer': 500,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy2.extensions.downloadstats.DownloadStats': 530,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'search.pipelines.AirasiaSearchPipeline': 300,
    'com.backends.redisbackend.Redis': 300
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
# AUTOTHROTTLE_ENABLED=True
# The initial download delay
# AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED=True
# HTTPCACHE_EXPIRATION_SECS=0
# HTTPCACHE_DIR='httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES=[]
# HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
