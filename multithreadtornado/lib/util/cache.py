#!/usr/bin/python
#coding=utf-8
# author Rowland
import threading
import time

CACHE_SIZE = 999


class Cache(object):
    '''
        lru缓存采用了lru算法，数据结构为单向链表，命中的节点会被直接提升为头结点
        受python递归栈约束，故将缓存容量设置为999，要使用更大值需设置递归深度值
    '''
    _lock = threading.Lock()
    _sentry = {}
    _index = []
    _count = 0

    @classmethod
    def fifo(cls, **kw):
        raise Exception('not implemented')

    @classmethod
    def lookup_node(cls, prev, sentry, key):
        if not sentry or not key:
            return None
        if sentry['key'] == key:
            with Cache._lock:
                if prev:
                    prev['next'] = sentry['next']
                    sentry['next'] = Cache._sentry
                    Cache._sentry = sentry
            return sentry
        return Cache.lookup_node(sentry, sentry['next'], key)

    @classmethod
    def set_node(cls, node):
        if not node:
            return
        with Cache._lock:
            node['next'] = Cache._sentry
            Cache._sentry = node

    @classmethod
    def lru(cls, **kw):
        ttl = kw.get('ttl', 10)

        def deco_func(func):
            def deco_args(*argv, **kwargv):
                #TODO 优化方法+参数的签名，TTL过期时间判定
                argvs = map(str, argv)
                if argv:
                    try:
                        if getattr(argv[0], func.__name__):
                            argvs = map(str, argv[1:])
                    except:
                        pass
                kv = str(kwargv)
                key = func.__module__ + '|' + argv[0].__class__.__name__ + '|' + func.__name__ + '|' + ''.join(
                    argvs) + '|' + kv
                #print key
                v_node = Cache.lookup_node(None, Cache._sentry, key)
                if not v_node:
                    #miss
                    v = func(*argv, **kwargv)
                    v_node = {
                        'key': key,
                        'value': v,
                        'timestamp': time.time()
                    }
                    Cache.set_node(v_node)
                return v_node['value']

            return deco_args

        return deco_func
