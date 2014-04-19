#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:46

import logging
import logging.config
import os
import httplib
import urllib


class Log():
    logger = None

    @classmethod
    def set_up(cls, log_cnf):
        logging.config.fileConfig(log_cnf['config_file'])
        Log.logger = logging.getLogger(log_cnf['default_logger'])

    def getLog(self):
        # todo: 不要写死simple这个logger
        if Log.logger == None:
            Log.logger = logging.getLogger('simple')
        return Log.logger


class HttpRequest:
    def __init__(self, host, **kwargs):
        if "timeout" not in kwargs:
            kwargs.update({"timeout":8})
        self.con = httplib.HTTPConnection(host, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.con.close()

    def connect(self):
        return self.con

    @staticmethod
    def url_encode(str):
        s = urllib.urlencode({"x":str})
        return s[len("x="):]

    def post(self, path, data):
        try:
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            params = None
            if data and type(data) is dict:
                params = urllib.urlencode(data)

            self.con.request("POST", path, params, headers)
            resp = self.con.getresponse()
            resp_str = resp.read()
            resp.close()
        except Exception as ex:
            raise ex
        finally:
            if resp:
                resp.close()
        return resp_str


def test():
    with HttpRequest(host="www.500.com") as conn:
        conn.post()
    #httpRequest = HttpRequest(host="www.500.com")
    #resp = httpRequest.post(path="/static/info/index/zxdj/zxdj.xml", data=None)
    #print resp.read()


