# coding: utf-8

configs = {
}


def set_up(confs):
    """设置默认（连接）参数
    """
    configs.update(confs)


########################################


import redis


redis_pools = {}


def get_redis(dbid, standalone=False):
    conf = configs['redis'][dbid].copy()
    if standalone:
        conf.pop('max_connections', None)
        return redis.Redis(**conf)
    pool = redis_pools.get(dbid)
    if not pool:
        conf.setdefault('max_connections', 8)
        pool = redis.ConnectionPool(**conf)
        redis_pools[dbid] = pool
    return redis.Redis(connection_pool=pool)



