#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:46
import os
import logging
import logging.config
from configer import Configer
import path


@Configer.register_my_setup(look='logging', level=1)
def set_up(cfg):
    log_path = os.path.join(path._ETC_PATH, cfg['config_file'])
    logging.config.fileConfig(log_path)
    Log.logger = logging.getLogger(cfg['default_logger'])


class Log():
    logger = None

    def getLog(self):
        return Log.logger


class XMLUtils(object):

    def parseElement(self, e):
        ret = {}
        if e.text:
            ret['text'] = e.text
        if e.attrib:
            ret['attr'] = e.attrib
        for i in e.iterchildren():
            ret.update({i.tag: self.parseElement(i)})
        return ret
