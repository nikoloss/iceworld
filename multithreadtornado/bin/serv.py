#!/usr/bin/python2.6
#coding=utf-8
#app path build-ups
# author Rowland
# edit 2014-03-19 14:17:30

import os
import sys
import json
import getopt
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'lib'))

import tornado.ioloop
import tornado.web
from tornado.log import access_log

from tools import Log, XMLUtils
from lxml import etree

import route
from configer import *

class Xroute(tornado.web.RequestHandler):
    '''通用预处理'''
    def prepare(self):
        # 获得正确的客户端ip
        ip = self.request.headers.get("X-Real-Ip", self.request.remote_ip)
        ip = self.request.headers.get("X-Forwarded-For", ip)
        ip = ip.split(',')[0].strip()
        self.request.remote_ip = ip
        # 允许跨域请求
        req_origin = self.request.headers.get("Origin")
        if req_origin:
            self.set_header("Access-Control-Allow-Origin", req_origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header("Allow", "GET, HEAD, POST")
            if self.request.method == "OPTIONS":
                self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
                self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type")
                self.finish()
                return
            else:
                self.set_header("Cache-Control", "no-cache")
        # json格式请求
        if self.request.headers.get('Content-Type', '').find("application/json") >= 0:
            try:
                self.json_args = json.loads(self.request.body)
            except Exception as ex:
                self.send_error(400)
        # xml格式请求
        elif self.request.headers.get('Content-Type', '').find('application/xml') >= 0:
            try:
                xu = XMLUtils()
                xml = self.request.body
                root = etree.fromstring(xml)
                root_dict = xu.parseElement(root)
                self.json_args = root_dict
            except Exception, e:
                self.send_error(501)
        # 普通参数请求
        elif self.request.arguments:
            self.json_args = dict((k, v[-1]) for k, v in self.request.arguments.items())

    @tornado.web.asynchronous
    def get(self, path):
        route.Router.get(path, self)
        
    @tornado.web.asynchronous
    def post(self, path):
        route.Router.post(path, self)
        
    @tornado.web.asynchronous
    def put(self, path):
        route.Router.put(path, self)
        
    @tornado.web.asynchronous
    def delete(self, path):
        route.Router.delete(path, self)

    @tornado.web.asynchronous
    def options(self, path):
        route.Router.options(path, self)


def get_application():
    """获取应用程序对象
    """
    return tornado.web.Application([(r"^/([^\.|]*)(?!\.\w+)$", Xroute)],
                log_function=log_request)


def log_request(handler):
    """http日志函数
    """
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    req = handler.request
    log_method('"%s %s" %d %s %.6f',
               req.method, req.uri, handler.get_status(),
               req.remote_ip, req.request_time() )

def init_application(conf_file):
    """初始化应用程序
    """
    cpff = ConfigParserFromFile()
    all_cfg = cpff.parseall(conf_file)
    Configer.setup(all_cfg)


if __name__=="__main__":
    # init
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    port = 8888
    includes = None
    opts, argvs = getopt.getopt(sys.argv[1:], "c:p:h")
    for op, value in opts:
        if op == '-c':
            includes = value
            path._ETC_PATH = os.path.dirname(os.path.abspath(value))
        elif op == '-p':
            port = int(value)
        elif op == '-h':
            print u'''使用参数启动:
                        usage: [-p|-c]
                        -p [prot] ******启动端口,默认端口:%d
                        -c <file> ******加载配置文件
                   ''' % port
            sys.exit(0)
    if not includes:
        includes = os.path.join(path._ETC_PATH, 'includes_dev.json')
        print "no configuration found!,will use [%s] instead" % includes
        # main
    init_application(includes)
    from serv import *
    application = get_application()
    application.listen(port)
    logger = Log().getLog()
    logger.info("starting..., listen [%d], configurated by (%s)", port, includes)
    tornado.ioloop.IOLoop.instance().start()


