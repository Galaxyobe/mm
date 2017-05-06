# -*- coding: UTF-8 -*-
"""
验证代理
"""

import json
import logging
import os
import random
import threading
import time
from multiprocessing.dummy import Pool as ThreadPool

import redis
import requests
from crontab import CronTab

# from twisted.internet import task 用task只能运行一次

logger = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.CRITICAL)


class Validate(object):
    """
    Validate class

    '''
    Validate Configure
    '''

    # 线程池 默认: 30
    POOLSIZE = 30

    # 可使用代理的最底分数 默认: 100
    # 计算方式为: int((score + base / cost) / 2)
    #   @param cost: 代理连接耗时 默认超时: 20s
    #   @param score: 上次得分
    #   @param base: 计算基数 默认: 1000
    USABLE_SCORE = 100

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
    """

    def __init__(self, settings, rpc=False):
        # self.__mutex = threading.Lock()
        self.__first_running = False
        self.__first_thread = None
        self.__circel_running = False
        self.__circel_thread = None
        self.__pid_running = False

        self.settings = settings
        param = settings.get('REDIS_PARAMS')
        if param:
            self.__redis_pool = redis.ConnectionPool(**param)
        else:
            logger.error('not set redis param')
            return

        self.__item_as_set = settings.getbool('REDIS_ITEM_AS_SET', False)
        self.__item_key = settings.get('REDIS_ITEMS_KEY')
        self.__validated_key = settings.get('REDIS_VALIDATE_KEY')
        self.exceptions = None
        self.pool_size = settings.getint('POOLSIZE', 30)
        self.usable_score = settings.getint('USABLE_SCORE', 100)
        self.usable_pid_count = settings.getint('USABLE_PID_COUNT', 50)
        self.__pid_interval = settings.getint('PID_INTERVAL', 10)
        self.get_ip_api = settings.get('GET_IP_API',
                                       'http://ip.taobao.com/service/getIpInfo.php?ip=%s')
        self.validate_url = settings.get('VALIDATE_URL',
                                         'https://www.baidu.com')
        self.project_path = settings.get('PROJECT_PATH')
        self.project_path = os.path.abspath(self.project_path)
        self.project_name = settings.get('BOT_NAME')
        self.__pid_file = '%s/%s' % (self.project_path, '.pid')
        # self.__pid(self.usable_pid_count, self.usable_score)
        # 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
        self.__cron = CronTab(user=True)
        self.__cron_comment = settings.get('CRONTAB_COMMENT')
        self.__cron_time = settings.get('CRONTAB_TIME')
        self.__cron_cmd = settings.get('CRONTAB_CMD')

        if rpc:
            self.circel_validate()

    def __cron_set(self):
        # 创建任务
        job = self.__cron.new(command=self.__cron_cmd % {'path': self.project_path},
                              comment=self.__cron_comment)
        # 设置任务执行周期
        job.setall(self.__cron_time)
        self.__cron.write()

    def __cron_cancel(self):
        # 任务注释 作为标识符
        comment = self.__cron_comment

        # 判断是否有一样的任务
        for job in self.__cron:
            if comment == job.comment:
                self.__cron.remove_all(comment=comment)

    def __pid(self, count, score):
        """
        PID执行线程
        维持可用代理的数量
        参数:
            @param count:
            @param score:
        返回:
            无
        """
        # print '__pid'
        try:
            client = redis.Redis(connection_pool=self.__redis_pool)
            num = int(client.zcount(self.__validated_key,
                                    score,
                                    '+inf'))

            # 停止抓取代理信息
            # twisted的反应堆不能在一个进程中重启的缘故，无法直接再次运行爬虫
            # 采用系统定时器的方法来启动抓取
            if num >= count:
                self.__cron_cancel()
            else:
                # 先处理已经抓取到的代理
                count = client.scard if self.__item_as_set else client.llen
                cnt = int(count(self.__item_key))
                if cnt > 0:
                    self.first_validate()
                else:
                    self.__cron_cancel()
                    self.__cron_set()

        except Exception, ex:
            print("#__pid %s:%s" % (Exception, ex))
        finally:
            pass

    def get(self, score, protocol=None, anonymousp=None):
        """
        随机获取一个可用分数的代理
        参数:
            @param score: 期望的分数
            @param protocol: 代理类型
            @param anonymousp: 代理的匿名情况
        返回:
            json: 代理信息
        """
        try:
            client = redis.Redis(connection_pool=self.__redis_pool)
            members = client.zrangebyscore(self.__validated_key,
                                           score,
                                           '+inf',
                                           0,
                                           self.usable_pid_count)
        except Exception, ex:
            print("@get %s:%s" % (Exception, ex))
        else:
            if members:
                while True:
                    member = json.loads(random.choice(members))
                    if isinstance(protocol, list):
                        if member['protocol'].lower() in protocol:
                            return member
                    elif isinstance(protocol, str):
                        if member['protocol'].lower() == protocol:
                            return member
                    else:
                        return json.loads(random.choice(members))
        return {}

    def __calc_score(self, cost, score=0, base=1000):
        """
        计算代理分数
        参数:
            @param cost: 代理连接耗时 默认超时: 20s
            @param score: 上次得分
            @param base: 计算基数 默认: 1000
        返回:
            int: 计算得分
        """
        return int((score + base / cost) / 2)

    def circel_validate(self):
        """
        循环验证
        """
        if self.__circel_running:
            return {'status': 'running'}
        self.__circel_thread = threading.Thread(target=self.__circel_validate)
        self.__circel_thread.setDaemon(True)
        self.__circel_thread.start()

        return {'status': 'started'}

    def __circel_validate(self):
        """
        循环验证入口
        验证__save_first_validated保存的代理
        """
        self.__circel_running = True
        times = 0
        poll = self.usable_pid_count / self.pool_size
        if poll < 3:
            poll = 10
        offset = 0
        __pool = ThreadPool(self.pool_size)
        client = redis.Redis(connection_pool=self.__redis_pool)
        while True:
            times += 1
            # print '__circel_validate'
            try:
                # 循环取数据
                datas = client.zrange(self.__validated_key,
                                      offset,
                                      offset + self.pool_size,
                                      withscores=True)

                # Network is unreachable
                if self.exceptions == -101:
                    time.sleep(10)

                if datas:
                    offset += self.pool_size + 1
                    results = __pool.map(self.__worker, datas)
                    self.__save_circel_validated(results)
                else:
                    offset = 0
                    time.sleep(5)
            except Exception, ex:
                print("#__circel_validate %s:%s" % (Exception, ex))
            finally:
                pass
            time.sleep(0.5)
            if times % poll:
                self.__pid(self.usable_pid_count, self.usable_score)
        # while结束
        __pool.close()
        __pool.join()
        self.__circel_running = False

    def __save_circel_validated(self, results):
        """
        保存循环验证成功的代理信息
        保存数据到redis，结构为zset
        键名: __validated_key
        参数:
            @param results: 一个list保持通过验证的代理信息
        """
        if not results:
            return

        try:
            client = redis.Redis(connection_pool=self.__redis_pool)

            for result in results:
                # print result
                (validated, cost) = result[0]
                # score为redis取出的分数
                (member, score) = result[1]

                # Network is unreachable
                if cost == -101:
                    self.exceptions = -101
                    return
                # print member, score
                # 验证成功
                if validated:
                    score = self.__calc_score(cost, score=score)
                else:
                    score = int(score)
                    # 删除失败次数过多的成员
                    if score < -20:
                        # print 'delete: %s' % (member)
                        client.zrem(self.__validated_key, member)
                        return
                    # 验证失败次数统计
                    elif score > 0:
                        score = -1
                    else:
                        score -= 1
                # 更新数据
                # print member, score
                client.zadd(self.__validated_key,
                            member,
                            score)
        except Exception, ex:
            print('@__save_passed %(except)s:%(ex)s', {
                'except': Exception, 'ex': ex})

    def first_validate(self):
        """
        开始初步验证
        """
        if self.__first_running:
            return {'status': 'running'}
        self.__first_thread = threading.Thread(target=self.__first_validate)
        self.__first_thread.setDaemon(True)
        self.__first_thread.start()
        return {'status': 'started'}

    def __first_validate(self):
        """
        first_validate入口
        取出要验证的代理信息放入线程池进行初步验证
        验证成功就保存到redis
        验证失败则丢弃
        """
        try:
            self.__first_running = True
            __pool = ThreadPool(self.pool_size)

            while True:
                # print '__first_validate'
                client = redis.Redis(connection_pool=self.__redis_pool)

                fetch = client.spop if self.__item_as_set else client.lpop
                datas = []
                count = 0
                while count < self.pool_size:
                    data = fetch(self.__item_key)
                    if data:
                        count += 1
                        datas.append(data)
                    else:
                        break
                # Network is unreachable
                if self.exceptions == -101:
                    time.sleep(10)

                if datas:
                    results = __pool.map(self.__worker, datas)
                    self.__save_first_validated(results)
                else:
                    break
        except Exception as ex:
            print('@__first_validate %s:%s' % (Exception, ex))
            # traceback.print_exc()
        finally:
            __pool.close()
            __pool.join()
            self.__first_running = False

    def __save_first_validated(self, results):
        """
        保存验证成功的代理信息
        保存数据到redis，结构为zset
        键名: self.__validated_key
        参数:
            @param results: 一个list保持通过验证的代理信息
        """

        if not results:
            return

        try:
            client = redis.Redis(connection_pool=self.__redis_pool)
            # pipeline = client.pipeline()
            # passed = time.strftime('%Y-%m-%d %H:%M')

            for result in results:
                # print result
                (validated, cost) = result[0]
                member = result[1]
                # 验证成功
                if validated:
                    score = self.__calc_score(cost)
                    # pipeline.zadd(self.__validated_key,
                    #               member,
                    #               score)
                    # 只增加不更新
                    client.execute_command('ZADD',
                                           self.__validated_key,
                                           'NX',
                                           score,
                                           member)
                else:
                    # Network is unreachable
                    if cost == -101:
                        self.exceptions = -101
                        # 把数据放回出处
                        save = client.sadd if self.__item_as_set else client.rpush
                        # pipeline.sadd(self.__item_key, member)
                        save(self.__item_key, member)
            # pipeline.execute()
        except Exception, ex:
            print('@__save_passed %(except)s:%(ex)s', {
                'except': Exception, 'ex': ex})

    def __worker(self, data):
        """
        处理验证的线程
        参数:
            @param data: 一条代理信息
        返回:
            Tuple: (results,data)
                results: doValidate()的返回值
                data: 传入的参数data
        """
        # self.__mutex.acquire()
        # print data
        # self.__mutex.release()
        try:
            if isinstance(data, tuple):
                item = data[0]
            else:
                item = data
            item = json.loads(item)
            # self.__mutex.acquire()
            # print "__worker:", item
            # self.__mutex.release()

            host = item['ip'].encode("UTF-8")
            port = item['port'].encode("UTF-8")
            protocol = item['protocol'].encode("UTF-8")

            results = self.doValidate(host, port, protocol)

            # self.__mutex.acquire()
            # print results, item
            # self.__mutex.release()

        except Exception, ex:
            print('@__worker %s:%s' % (Exception, ex))
            # traceback.print_exc()
        else:
            return results, data

    def doValidate(self, host, port, protocol='http', timeout=20):
        """
        验证代理
        参数:
            @param host:
            @param port:
            @param protocol: http/https
            @param timeout:
        返回:
            Tuple: (validated,cost)
                validated: True/False
                score: float/int 负数表示错误
                验证成功: True,cost
                验证失败: False,errno
        """
        # 格式
        # proxies = {
        #   'http': 'http://10.10.1.10:3128',
        #   'https': 'https://10.10.1.10:1080',
        # }
        protocol = protocol.lower()
        proxies = {}
        proxies[protocol] = '{protocol}://{host}:{port}'.format(protocol=protocol,
                                                                host=host,
                                                                port=port)

        # self.__mutex.acquire()
        # print proxies
        # self.__mutex.release()

        # 第一步 用代理ip去获取ip地址
        # 第二步 访问一个网页进行初步验证
        step = 0
        while True:
            try:

                start_timestamp = time.time()

                url = self.get_ip_api % host
                if step == 1:
                    url = self.validate_url
                    # url = 'https://www.baidu.com'

                req = requests.get(url, proxies=proxies, timeout=timeout)

            except requests.exceptions.ConnectTimeout as ex:
                # print 'ConnectTimeout:', ex
                return False, -110
            except requests.exceptions.ReadTimeout as ex:
                # print 'ReadTimeout:', ex
                return False, -111
            except requests.exceptions.ProxyError as ex:
                # print 'ProxyError:', ex
                e = ex.__str__()
                if e.find('Errno 101') > 0:
                    return False, -101
                else:
                    # 500 通用错误
                    return False, -100
            except:
                # 500 通用错误
                return False, -109
            else:
                if req.status_code == 200:
                    # print req.content
                    if step == 0:
                        if req.content.find(host) > 0:
                            step += 1
                        else:
                            # 500 通用程序
                            return False, -100
                    elif step == 1:
                        cost = time.time() - start_timestamp
                        return True, float('%0.3f' % cost)
                else:
                    # 500 通用错误
                    return False, -100
