#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
命令解析
"""


import argparse
import os
import os.path
import signal
import subprocess
import time

import psutil
import redis
from configparser import ConfigParser

from com.airasia.search import AirasiaSearch
from com.utils.key import KeyGenerator

today = time.strftime('%Y-%m-%d', time.localtime(time.time()))


def generate_url(args):
    """
    生成URL
    """

    print 'generate_url', args

    search_queue_key = 'airasia:search:queue'

    REDIS_START_URLS_AS_SET = True
    REDIS_START_URLS_IS_ZSET = True

    redis_param = {
        'host': '127.0.0.1',
        'port': 6379
    }
    redis_param.update(dict(x.split('=', 1) for x in args.redis))

    server = redis.Redis(**redis_param)

    search = AirasiaSearch()

    keyGenerator = KeyGenerator()

    params = {}

    if 'airasia' in args.source:
        params = {'o1': args.depart.upper(),
                  'd1': args.arrive.upper(),
                  'dd1': args.date,
                  'ADT': args.adult,
                  'CHD': args.children,
                  'inl': args.infant}
        # 返程处理
        # 有返程时，是不会把单程日期拆分为同一个的单程和返程
        if args.return_date:
            params['dd2'] = args.return_date
        # 语种处理
        if args.language == 'en':
            params['culture'] = 'en-GB'
        elif args.language == 'zh':
            params['culture'] = 'zh-CN'

    params['days'] = args.days
    params['round'] = args.round

    urls = search.generate_urls(**params)

    for url, date in urls:

        priority = 100.0

        if REDIS_START_URLS_IS_ZSET:
            server.zadd(search_queue_key, url, priority)
        else:
            save_one = server.sadd if REDIS_START_URLS_AS_SET else server.lpush
            save_one(search_queue_key, url)

        date = '%s 23:59:59' % date
        timestamp = int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))

        data = {'priority': priority,
                'expire': timestamp}

        url_key = keyGenerator.generator_data_key(url)
        server.hmset(url_key, data)
        server.expireat(url_key, timestamp)

        print url, date


def search_file(rootdir, filename):
    """
    在选定目录下查找文件名，返回文件所在的目录及路径

    参数:
        @rootdir: 查找的根目录
        @filename: 匹配的文件名
    返回:
        tuple: (parent, filepath)
            parent: 文件所在的目录
            filepath: 文件所在的路径
    """
    for parent, _, filenames in os.walk(rootdir):
        for _filename in filenames:
            if _filename == filename:
                filepath = os.path.join(parent, _filename)
                yield parent, filepath


def spider_run(args):
    """
    运行爬虫
    """
    # print 'spider_run', args

    if args.log_level_debug:
        args.settings.append('LOG_LEVEL=DEBUG')

    if args.log_path:
        args.log_path = os.path.abspath(args.log_path)
        if not os.path.isdir(args.log_path):
            os.mkdir(args.log_path)
        logfile = '%(path)s/%(name)s-%(date)s-%(id)s.log'

    # TODO:传入各个爬虫的实例数量
    configParser = ConfigParser()
    currentpath = args.path
    configs = search_file(rootdir=currentpath, filename='scrapy.cfg')
    # 获取爬虫部署名称及实例数量
    deploys = []
    for parent, configfile in configs:
        try:
            with open(configfile) as _file:
                configParser.readfp(_file)
                deploy = {}
                deploy['name'] = configParser.get('deploy', 'project')
                deploy['replicas'] = configParser.getint('deploy', 'replicas')
                deploy['path'] = parent
        except:
            pass

        if not deploy['replicas']:
            deploy['replicas'] = 1

        if args.name:
            if deploy['name'] in args.name:
                deploys.append(deploy)
        else:
            deploys.append(deploy)

    date_time = time.strftime('%Y%m%d%H%M%S',
                              time.localtime(time.time()))

    # 运行爬虫实例
    for deploy in deploys:

        os.chdir(deploy['path'])

        for idx in range(deploy['replicas']):

            _settings = args.settings[:]

            if args.log_path:
                _logfile = logfile % {'path': args.log_path,
                                      'name': deploy['name'],
                                      'date': date_time,
                                      'id': idx + 1}
                _settings.append('LOG_FILE=%s' % _logfile)
            param = ['scrapy', 'crawl', deploy['name']]
            if args.settings:
                for item in _settings:
                    param.append('-s')
                    param.append(item)
            subprocess.Popen(param)


def get_scrapy_process(display=False):
    """
    获取scrapy的进程信息
    """
    pids = psutil.pids()

    run_list = []

    for pid in pids:
        try:
            infos = psutil.Process(pid).as_dict(
                attrs=['pid', 'name', 'cmdline', 'num_threads'])
        except:
            pass
        else:
            if 'scrapy' in infos['name']:
                if display:
                    print infos
                run_list.append(infos)

    return run_list


def spider_list(args):
    """
    运行的爬虫列表
    """
    # print 'spider_list', args

    while True:
        try:

            run_list = get_scrapy_process()
            if run_list:
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            for runner in run_list:
                if args.name:
                    for name in args.name:
                        if name in runner['cmdline']:
                            print runner
                else:
                    print runner
            if not args.keep:
                break
            else:
                print '-' * 80
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print ''
            return


def spider_stop(args):
    """
    停止运行爬虫
    """
    # print 'spider_stop', args

    if args.numbers > 0:
        print '暂时不支持 -N | --numbers选项'
        return

    _signal = signal.SIGTERM
    if args.force:
        _signal = signal.SIGKILL

    run_list = get_scrapy_process()

    kill_all = 0

    for runner in run_list:
        if args.name:
            for name in args.name:
                if name in runner['cmdline']:
                    print '正在发生结束信号:[%s]\n%s' % (_signal, runner)
                    os.kill(runner['pid'], _signal)
        else:
            while kill_all == 0:
                answer = raw_input("准备结束所有的scrapy进程？:Y/N\n")
                if answer.upper() == 'Y':
                    kill_all = 1
                else:
                    print '\n已取消操作'
                    return
            if kill_all > 0:
                print '正在发生结束信号:[%s]\n%s' % (_signal, runner)
                os.kill(runner['pid'], _signal)


def monitor(args):
    """
    监控爬虫运行结果
    """
    redis_param = {
        'host': '127.0.0.1',
        'port': 6379
    }

    for item in args.redis:
        kv = item.split('=')
        if len(kv) == 2:
            redis_param[kv[0]] = kv[-1]

    server = redis.Redis(**redis_param)

    while True:
        try:
            datas = server.keys(args.key)
            datas.sort()
            print len(datas)
            print '-' * 80
            if args.detailed:
                for data in datas:
                    print '|-', data
                print len(datas)
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print ''
            return


# 命令解析
parser = argparse.ArgumentParser(description='爬虫命令')

subparsers = parser.add_subparsers(help='commands')

# 生成URL命令
generate_parser = subparsers.add_parser('gen', help='爬虫URL生成器')

generate_parser.add_argument('-s', '--source',
                             dest='source',
                             default=[],
                             action='store',
                             choices=('airasia'),
                             nargs='+',
                             metavar='airasia',
                             required=True,
                             help='数据来源')
generate_parser.add_argument('-d', '--depart',
                             dest='depart',
                             action='store',
                             metavar='CAN',
                             required=True,
                             help='出发地')
generate_parser.add_argument('-a', '--arrive',
                             dest='arrive',
                             action='store',
                             metavar='DEL',
                             required=True,
                             help='抵达地')
generate_parser.add_argument('-dd', '--date',
                             dest='date',
                             action='store',
                             default=today,
                             metavar=today,
                             help='出发时间')
generate_parser.add_argument('-rd', '--return-date',
                             dest='return_date',
                             action='store',
                             default=None,
                             metavar=today,
                             help='返程时间')
generate_parser.add_argument('-D', '--days',
                             dest='days',
                             type=int,
                             default=1,
                             action='store',
                             metavar='days',
                             help='重复天数')

# 把单程日期拆分为同一天的单程和返程
# 仅仅对单程有效
# A->B D => A->B D | B->A D
generate_parser.add_argument('--no-round',
                             dest='round',
                             action='store_false',
                             help='禁止单程变双程')
generate_parser.add_argument('-A', '--adult',
                             dest='adult',
                             type=int,
                             default=1,
                             action='store',
                             metavar='numbers',
                             help='成人数量')
generate_parser.add_argument('-C', '--children',
                             dest='children',
                             type=int,
                             default=1,
                             action='store',
                             metavar='numbers',
                             help='儿童数量')
generate_parser.add_argument('-I', '--infant',
                             dest='infant',
                             type=int,
                             default=1,
                             action='store',
                             metavar='numbers',
                             help='婴儿数量')
generate_parser.add_argument('-l', '--language',
                             dest='language',
                             default='en',
                             choices=('zh', 'en'),
                             action='store',
                             metavar='language',
                             help='语言')
generate_parser.add_argument('--set-redis',
                             default=[],
                             dest='redis',
                             nargs='+',
                             action='store',
                             metavar="host='127.0.0.1' port=6379 db=0",
                             help='redis设置')
# 设置处理函数
generate_parser.set_defaults(func=generate_url)

# 运行爬虫命令
run_parser = subparsers.add_parser('run', help='运行爬虫')

run_parser.add_argument('--path',
                        dest='path',
                        default=os.getcwd(),
                        action='store',
                        metavar=os.getcwd(),
                        help='爬虫所在的路径')
run_parser.add_argument('-n', '--name',
                        dest='name',
                        action='store',
                        nargs='+',
                        metavar='spider name',
                        help='爬虫名称')
run_parser.add_argument('-s', '--settings',
                        dest='settings',
                        default=[],
                        action='store',
                        nargs='+',
                        metavar='spider settings',
                        help='爬虫参数设置')
run_parser.add_argument('-D', '--log-level',
                        dest='log_level_debug',
                        action='store_true',
                        help='使能调试')
run_parser.add_argument('-l', '--log-path',
                        dest='log_path',
                        default=None,
                        action='store',
                        help='日志路径')
# run_parser.add_argument('-R', '--repeat',
#                         dest='repeat',
#                         default=1,
#                         type=int,
#                         action='store',
#                         metavar='numbers',
#                         help='运行的实例数量')
# 设置处理函数
run_parser.set_defaults(func=spider_run)

# 停止运行爬虫命令
stop_parser = subparsers.add_parser('stop', help='停止运行爬虫')

stop_parser.add_argument('-n', '--name',
                         dest='name',
                         action='store',
                         nargs='+',
                         metavar='spider name',
                         help='爬虫名称')
stop_parser.add_argument('-f', '--force',
                         dest='force',
                         action='store_true',
                         help='是否强制结束')
stop_parser.add_argument('-N', '--numbers',
                         dest='numbers',
                         default=0,
                         type=int,
                         action='store',
                         metavar='numbers',
                         help='停止的实例数量')
# 设置处理函数
stop_parser.set_defaults(func=spider_stop)

# 爬虫运行列表命令
list_parser = subparsers.add_parser('list', help='爬虫运行列表')

list_parser.add_argument('-n', '--name',
                         dest='name',
                         action='store',
                         nargs='+',
                         metavar='spider name',
                         help='爬虫名称')
list_parser.add_argument('-k', '--keep',
                         dest='keep',
                         action='store_true',
                         help='持续监控')
list_parser.add_argument('-i', '--interval',
                         type=int,
                         default=5,
                         dest='interval',
                         action='store',
                         metavar='seconds',
                         help='刷新间隔')
# 设置处理函数
list_parser.set_defaults(func=spider_list)

# 监控爬虫运行结果命令
monitor_parser = subparsers.add_parser('mon', help='爬虫运行列表')

monitor_parser.add_argument('-k', '--key',
                            dest='key',
                            default='*:*:*:*:*',
                            action='store',
                            metavar='name',
                            help='Redis键')
monitor_parser.add_argument('-i', '--interval',
                            type=int,
                            default=5,
                            dest='interval',
                            action='store',
                            metavar='seconds',
                            help='刷新间隔')
monitor_parser.add_argument('-d', '--detailed',
                            dest='detailed',
                            action='store_true',
                            help='列出详情')
monitor_parser.add_argument('--set-redis',
                            dest='redis',
                            default=[],
                            nargs='+',
                            action='store',
                            metavar="host='127.0.0.1' port=6379 db=0",
                            help='redis设置')
# 设置处理函数
monitor_parser.set_defaults(func=monitor)

# 处理命令
results = parser.parse_args()
results.func(results)
