#!/usr/bin/python
#coding=utf-8
# author Rowland
import threading, time, pickle
import db_util

CACHE_SIZE = 1000

def redcache(**kw):
    '''
       redis cache
    '''
    ttl = kw.get('ttl',60)
    def deco_func(func):
        def deco_args(*argv,**kwargv):
            argvs = map(str, argv)
            if argv:
                try:
                    if getattr(argv[0], func.__name__):
                        argvs = map(str, argv[1:])
                except:
                    pass
            kv = str(kwargv)
            key = __file__ + '|' + func.__name__ + '|' + ''.join(argvs) + '|' + kv
            r = db_util.get_redis('main')
            value = r.get(key)
            #print key,'======',value
            if value:
                #r.delete(key)
                #print 'hit! [%s]' % key
                try:
                    return pickle.loads(value)
                except:
                    r.delete(key)
            ret = func(*argv,**kwargv)
            if ret:
                #pass
                r.set(key, pickle.dumps(ret), ttl)
            #print "cached!"
            return ret
        return deco_args
    return deco_func

class MemCache(object):
    _lock = threading.Lock()
    _cache = {}
    _index = []
    _count = 0
    class __Node(object):
        def __init__(self, value):
            self.value = value
            self.access_time = time.time()
        def __repr__(self):
            return `self.value` + '=' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.access_time))

    @classmethod
    def fifo(cls, **kw):
        raise Exception('not implemented')
    
    @classmethod
    def lru(cls, **kw):
        ttl = kw.get('ttl',10)
        def deco_func(func):
            def deco_args(*argv, **kwargv):
                argvs = map(str,argv)
                if argv:
                    try:
                        if getattr(argv[0], func.__name__):
                            argvs = map(str, argv[1:])
                    except:
                        pass
                kv = str(kwargv)
                key = __file__ + '|' +func.__name__ + '|' + ''.join(argvs) + '|' + kv
                cached_node = MemCache._cache.get(key)
                #print key
                if cached_node:
                    if (time.time() - cached_node.access_time) < ttl:
                        #print "hit"
                        #hit ,refresh
                        MemCache.refresh_cache(key)
                        return cached_node.value
                    else:
                        #print "hit but expire"
                        #hit but expired! delete
                        MemCache.del_cache(key)
                        ret = func(*argv,**kwargv)
                        if ret:
                            #new cache
                            MemCache.new_cache(key, ret)
                        return ret
                else:
                    #print "miss"
                    #miss! 
                    #check size if cache pool not full
                    #directly put
                    #if full , delete key by LRU algorithm 
                    ret = func(*argv,**kwargv)
                    if ret:
                        if MemCache._count < CACHE_SIZE :
                            MemCache.new_cache(key, ret)
                        else :
                            MemCache.lru_del_cache()
                            MemCache.new_cache(key, ret)
                        return ret
            return deco_args
        return deco_func

    @classmethod
    def is_expired(cls, key):
        cached_node = MemCache._cache.get(key)
        if not cached_node:
            return True
        return (time.time() - cached_node.access_time) > ttl

    @classmethod
    def new_cache(cls, key, value):
        with MemCache._lock:
            MemCache._cache[key] = MemCache.__Node(value)
            MemCache._index.append(key)
            MemCache._count += 1
            #print "new %s INDEX:" % key, MemCache._index

    @classmethod
    def del_cache(cls, key):
        with MemCache._lock:
            MemCache._cache.pop(key)
            MemCache._index.remove(key)
            MemCache._count -= 1
            #print "del %s INDEX:" % key, MemCache._index

    @classmethod
    def lru_del_cache(cls):
        with MemCache._lock:
            key = MemCache._index.pop(0)
            MemCache._cache.pop(key)
            MemCache._count -= 1
            #print "lru %s INDEX:" % key, MemCache._index

    @classmethod
    def refresh_cache(cls, key):
        with MemCache._lock:
            MemCache._index.remove(key)
            MemCache._index.append(key)
            #print "ref %s INDEX:" % key, MemCache._index

