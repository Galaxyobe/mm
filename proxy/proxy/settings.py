# -*- coding: utf-8 -*-

# Scrapy settings for proxy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'proxy'

# SPIDER_MODULES = ['proxy.spiders']
# NEWSPIDER_MODULE = 'proxy.spiders'

LOG_LEVEL = 'INFO'

# Configure custom commands
# See
# https://doc.scrapy.org/en/latest/topics/commands.html#custom-project-commands
COMMANDS_MODULE = 'proxy.commands'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'proxy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

"""
Redis Configure
"""
# Specify the host and port to use when connecting to Redis (optional).
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
REDIS_PARAMS = {
    'host': 'localhost',
    'port': 6379,
    'db': 2,
    'password': 'datacenter.io',
}

REDIS_ITEMS_KEY = 'proxy:items'
REDIS_VALIDATE_KEY = 'proxy:validated'
REDIS_ITEM_AS_SET = True


"""
RPC Configure
"""
# Configure RPC
RPC_PARAMS = {
    'ip': '127.0.0.1',
    'port': 4242,
}

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html# download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False


"""
Validate Configure
"""

# 线程池 默认: 30
POOLSIZE = 30

# 可使用代理的最底分数 默认: 100
# 计算方式为: int((score + base / cost) / 2)
#   @param cost: 代理连接耗时 默认超时: 20s
#   @param score: 上次得分
#   @param base: 计算基数 默认: 1000
USABLE_SCORE = 100

# 使用代理的概率 默认: 70(0-100)
# 0-不使用代理 70-70%的链接使用代理访问
USABLE_PROBABILITY = 80

# 保持可用的数量 默认: 50
USABLE_PID_COUNT = 100

# PID检测间隔 默认:10s
PID_INTERVAL = 10

# 查询IP接口 %s为填充的ip地址
GET_IP_API = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'

# 检测代理有效性的网址
# VALIDATE_URL = 'https://booking.airasia.com'
VALIDATE_URL = 'https://www.baidu.com'

# 项目路径
PROJECT_PATH = '.'
# pid文件
PID_NAME = '.pid'

# cron任务注释 作为标识符
CRONTAB_COMMENT = 'proxy'
# cron任务定时时间
CRONTAB_TIME = '*/15 * * * *'
# cron任务命令
CRONTAB_CMD = 'python %(path)s/run-crawler.py'


# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'proxy.middlewares.ProxySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy2.downloadermiddlewares.rotateuseragent.RotateUserAgentMiddleware': 400,
    'scrapy2.downloadermiddlewares.rpcproxy.RPCProxyMiddleware': 400,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy2.pipelines.redis.RedisPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html# httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
