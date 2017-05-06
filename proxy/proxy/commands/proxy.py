# -*- coding: utf-8 -*-
"""
scrapy自定义命令
"""
import logging

from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.project import get_project_settings

from org.utils.rpc import RPCServer

from .crawler import RunCrawler
from .validate import Validate


logger = logging.getLogger(__name__)


class ProxyCommand(ScrapyCommand):
    """
    ProxyCommand class
    """
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    def __init__(self):
        super(ProxyCommand, self).__init__()
        self.settings = get_project_settings()

    def short_desc(self):
        return 'run spider by rule'

    def syntax(self):
        return '[options]'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        # 运行验证程序
        parser.add_option(
            "-r",
            dest="validate",
            default=False,
            action="store_true",
            help="run validate")
        # 运行循环验证程序
        parser.add_option(
            "-l",
            dest="circle",
            default=False,
            action="store_true",
            help="run circle validate")
        # 运行抓取程序
        parser.add_option(
            "-c",
            dest="crawl",
            default=False,
            action="store_true",
            help="run spider crawl")
        # 运行RPC程序
        parser.add_option(
            "--rpc",
            dest="rpc",
            default=False,
            action="store_true",
            help="run rpc server")
        # 测试RPC程序
        parser.add_option(
            "--rpc-test",
            dest="rpc_test",
            default=False,
            action="store_true",
            help="test rpc server")
        # 后台运行抓取程序
        # parser.add_option(
        #     "-d",
        #     dest="crawl_backend",
        #     default=False,
        #     action="store_true",
        #     help="run spider crawl in backend")
        # parser.add_option(
        #     "-a",
        #     dest="spargs",
        #     action="append",
        #     default=[],
        #     metavar="NAME=VALUE",
        #     help="set spider argument (may be repeated)")
        # parser.add_option(
        #     "-o",
        #     "--output",
        #     metavar="FILE",
        #     help="dump scraped items into FILE (use - for stdout)")
        # parser.add_option(
        #     "-t",
        #     "--output-format",
        #     metavar="FORMAT",
        #     help="format to use for dumping items with -o")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            pass

        except ValueError:
            raise UsageError(
                "Invalid -a value, use -a NAME=VALUE", print_help=False)

    def run(self, args, opts):
        """
        Entry point for running commands
        """

        if opts.circle:
            if opts.rpc:
                param = self.settings.get('RPC_PARAMS')
                if not param:
                    print 'not set rpc param'
                else:
                    try:
                        param['methods'] = Validate(self.settings, rpc=True)
                        RPCServer(**param)
                    except Exception as ex:
                        print ex
            else:
                validate = Validate(self.settings)
                validate.circel_validate()
        elif opts.crawl:
            crawler = RunCrawler()
            crawler.start()
        elif opts.rpc_test:
            import time
            from org.utils.rpc import RPCClient
            param = self.settings.get('RPC_PARAMS')
            if not param:
                print 'not set rpc param'
            rpc = RPCClient(**param)
            client = rpc.getClient()
            try:
                while True:
                    print client.get(0)
                    time.sleep(5)
            except Exception as ex:
                print ex
            finally:
                rpc.close()
