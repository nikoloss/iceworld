#!/usr/bin/python
#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:32
import os, inspect, sys, re, json, time
import path, threading
import traceback

import tornado.ioloop, tornado.web
from concurrent import futures

from util.tools import Log


executor = futures.ThreadPoolExecutor(max_workers=16)
log=Log().getLog()


def _call_wrap(call, params):
    try:
        ret = call(*params)
    except Exception as ex:
        log.exception('error')
        tornado.ioloop.IOLoop.instance().add_callback(lambda:params[0].send_error())
    tornado.ioloop.IOLoop.instance().add_callback(lambda:params[0].finish(ret))



class Router(object):   
    '''dispather and decortor'''
    _GET    =    0x001
    _POST   =    0x002
    _PUT    =    0x004
    _DELETE =    0x008
    mapper={} 
    @classmethod
    def route(cls,**deco):
        def foo(func):
            #print func.__name__,inspect.stack()[1][3],func.__module__
            url = deco.get('url') or '/'
            if url not in Router.mapper:
                method = deco.get('method') or Router._GET
                mapper_node = {}
                mapper_node['method'] = method
                mapper_node['callName'] = func.__name__
                mapper_node['className'] = inspect.stack()[1][3]
                mapper_node['moduleName'] = func.__module__
                Router.mapper[url] = mapper_node
            return func
        return foo
    @classmethod
    def get(cls,path,reqhandler):
        Router.emit(path, reqhandler, Router._GET)
    @classmethod
    def post(cls,path,reqhandler):
        Router.emit(path, reqhandler, Router._POST)
    @classmethod
    def put(cls,path,reqhandler):
        Router.emit(path, reqhandler, Router._PUT)
    @classmethod
    def delete(cls,path,reqhandler):
        Router.emit(path, reqhandler, Router._DELETE)        
    @classmethod
    def emit(cls,path,reqhandler,method_flag):
        mapper = Router.mapper
        for urlExp in mapper:
            m = re.match('^'+urlExp+'$',path)
            if m:
                params = (reqhandler,)
                for items in m.groups():
                    params+=(items,)
                mapper_node = mapper.get(urlExp)
                method = mapper_node.get('method')
                if method_flag != method_flag & method:
                    log.warn("method refuse!uri=%s,method=%d,parameters=|%s|", path, method_flag, reqhandler.request.arguments or "")
                    raise tornado.web.HTTPError(405)
                callName = mapper_node.get('callName')
                className = mapper_node.get('className')
                moduleName = mapper_node.get('moduleName')
                # -----------------------------
                module = __import__(moduleName)
                clazz = getattr(module, className)
                try:
                    obj = clazz()
                except Exception as e:
                    log.exception("error occured when creating instance of %s" % className)
                    raise tornado.web.HTTPError(500)
                call = getattr(obj, callName)
                if not call:
                    raise tornado.web.HTTPError(405)
                # -----------------------------
                log.info('%s %s', path, reqhandler.json_args or {})
                executor.submit(_call_wrap, call, params)
                break
        else:
            log.warn("not found!uri=%s,method=%d,parameters=|%s|", path, method_flag, reqhandler.request.arguments or "")
            raise tornado.web.HTTPError(404)
            
#automic scan dirs
files_list = os.listdir(path._BIZ_PATH)
files_list = set([x[:x.rfind(".")] for x in files_list if x.endswith(".py")])
#print files_list
map(__import__, files_list)
