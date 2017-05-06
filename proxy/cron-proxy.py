# -*- coding: utf-8 -*-
"""
定时运行
"""
import sys

from crontab import CronTab

from proxy.commands.crawler import RunCrawler

crawler = RunCrawler()
crawler.start()

path = sys.path[0]
# 任务注释 作为标识符
comment = 'proxy'
# 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
cron = CronTab(user=True)
# 判断是否有一样的任务
for job in cron:
    if comment == job.comment:
        cron.remove_all(comment=comment)
# 创建任务
job = cron.new(command='cd %s && python %s' %
               (path, __file__),
               comment=comment)
# 设置任务执行周期，每10分钟执行一次
job.setall('*/10 * * * *')
cron.write()
