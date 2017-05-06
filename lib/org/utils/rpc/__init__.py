# -*- coding: utf-8 -*-
"""
ZeroRPC服务
"""
from logging import getLogger

import zerorpc

# logger = getLogger(__name__)


class RPCServer(object):
    """
    RPCServer class
    """

    def __init__(self, ip='127.0.0.1', port=4242, methods=None):
        server = zerorpc.Server(methods)
        try:
            server.bind("tcp://%s:%s" % (ip, port))
            # logger.info('rpc start %(ip)s:%(port)s', {'ip': ip, 'port': port})
            server.run()
        except Exception, ex:
            pass
            # logger.error("%(except)s:%(ex)s", {'except': Exception, 'ex': ex})


class RPCClient(object):
    """
    RPCClient class
    """
    client = zerorpc.Client()

    def __init__(self, ip='127.0.0.1', port=4242):
        self.client.connect("tcp://%s:%s" % (ip, port))

    def getClient(self):
        """
        返回客户端
        """
        return self.client

    def close(self):
        """
        关闭连接
        """
        self.client.close()
