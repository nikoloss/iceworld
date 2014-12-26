#!/usr/bin/python
#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:32
# 虚拟路由总管，拦截请求转发请求到业务线程池
# edit 2014-12-15 18:02:09
# 修改映射表数据结构为单向链表（方便进行优化算法），增加URL冲突检测，优化性能精简代码，高负载下随机拒绝服务
import os, inspect, sys, re, time, random

import tornado.ioloop, tornado.web
from concurrent import futures
from itertools import groupby

import util.tools

MAX_WORKERS = 16

executor = futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)


def set_up(biz_dir):
    global logger
    logger = util.tools.Log().getLog()
    #automic scan dirs
    files_list = os.listdir(biz_dir)
    files_list = set([x[:x.rfind(".")] for x in files_list if x.endswith(".py")])
    map(__import__, files_list)
    Router.pre_check()

def _call_wrap(call, params):
    handler = params[0]
    try:
        #logger.info('request: %s %s', handler.request.path, handler.json_args or {})
        ret = call(*params)
        tornado.ioloop.IOLoop.instance().add_callback(lambda: params[0].finish(str(ret)))
    except Exception as ex:
        logger.exception(ex)
        tornado.ioloop.IOLoop.instance().add_callback(lambda: params[0].send_error())


class Router(object):
    '''dispather and decortor'''
    _GET = 0x001
    _POST = 0x002
    _PUT = 0x004
    _DELETE = 0x008
    _OPTIONS = 0x016
    mapper = []
    mapper_sentry = {}
    last_sentry = {}

    @classmethod
    def check_redefined_node(cls, sentry, url_exp, method):
        if not sentry:
            return None
        if sentry['eUrl'] == url_exp and sentry['method'] & method:
            return sentry
        else:
            return Router.check_redefined_node(sentry['next'], url_exp, method)

    @classmethod
    def lookup_suitable_node(cls, prev, sentry, url, method, assert_wrong_method=False):
        if not sentry:
            if assert_wrong_method:
                raise tornado.web.HTTPError(405)
            raise tornado.web.HTTPError(404)
        matcher = sentry['eUrl'].match(url)
        m = sentry['method']
        wrong = assert_wrong_method
        if matcher:
            if m & method: #hit!
                if prev:
                    prev['next'] = sentry['next']
                    sentry['next'] = Router.mapper_sentry
                    Router.mapper_sentry = sentry
                return sentry, matcher
            else:
                wrong = True
        return Router.lookup_suitable_node(sentry, sentry['next'], url, method, wrong)

    @classmethod
    def pre_check(cls):
        check_mapper_list = filter(lambda (x, y): len(y) > 1, [
            (key, list(items)) for key, items in
            groupby(Router.mapper,
                    lambda x: x)
        ]
        )
        if check_mapper_list:
            for check_mapper in check_mapper_list:
                logger.fatal('Definition conflict : FUNCTION[%s]', check_mapper[0])
            sys.exit(1)

    @classmethod
    def route(cls, **deco):
        def foo(func):
            url = deco.get('url') or '/'
            eUrl = re.compile('^' + url + '$', re.IGNORECASE)
            method = deco.get('method') or Router._GET
            if Router.check_redefined_node(Router.mapper_sentry, eUrl, method):
                logger.fatal('Definition conflict : URL[%s]', url)
                sys.exit(1)
            else:
                mapper_node = {
                    'eUrl': eUrl,
                    'method': method,
                    'callName': func.__name__,
                    'className': inspect.stack()[1][3],
                    'moduleName': func.__module__,
                    'next': {},
                }
                Router.mapper.append(
                    '.'.join([mapper_node['moduleName'], mapper_node['className'], mapper_node['callName']]))
                if Router.mapper_sentry:
                    Router.last_sentry['next'] = mapper_node
                    Router.last_sentry = Router.last_sentry['next']
                else:
                    Router.mapper_sentry = mapper_node
                    Router.last_sentry = Router.mapper_sentry
            return func

        return foo

    @classmethod
    def get(cls, path, reqhandler):
        Router.emit(path, reqhandler, Router._GET)

    @classmethod
    def post(cls, path, reqhandler):
        Router.emit(path, reqhandler, Router._POST)

    @classmethod
    def put(cls, path, reqhandler):
        Router.emit(path, reqhandler, Router._PUT)

    @classmethod
    def delete(cls, path, reqhandler):
        Router.emit(path, reqhandler, Router._DELETE)

    @classmethod
    def options(cls, path, reqhandler):
        Router.emit(path, reqhandler, Router._OPTIONS)

    @classmethod
    def verify_passport(cls):
        capacity = 0 if len(executor._threads) == 0 else executor._work_queue.qsize() / float(
            len(executor._threads))
        if 2 > capacity >= 1.0:
            #随机拒绝请求
            return False if (random.random() + 1) > capacity else True
        elif capacity >= 2:
            return False
        else:
            return True

    @classmethod
    def emit(cls, path, reqhandler, method_flag):
        if not Router.verify_passport():
            logger.warn("server is under high pressure ,[free thread:%d] [queue size:%d] [request refused %s]",
                        len(executor._threads),
                        executor._work_queue.qsize(),
                        path)
            ret = {
                'status': '99',
                'message': es_error.get_code_msg('99'),
                'data': {},
            }
            tornado.ioloop.IOLoop.instance().add_callback(lambda: reqhandler.finish(ret))
            return
        mapper_node, m = Router.lookup_suitable_node(None, Router.mapper_sentry, path, method_flag)
        if mapper_node and m:
            params = (reqhandler,)
            for items in m.groups():
                params += (items,)
            callName = mapper_node['callName']
            className = mapper_node['className']
            moduleName = mapper_node['moduleName']
            module = __import__(moduleName)
            clazz = getattr(module, className)
            try:
                obj = clazz()
            except Exception, e:
                logger.exception("error occured when creating instance of %s" % className)
                raise tornado.web.HTTPError(500)
            call = getattr(obj, callName)
            executor.submit(_call_wrap, call, params)

