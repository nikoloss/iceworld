#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:46

import logging
import logging.config


class Log():
    logger = None

    @classmethod
    def set_up(cls, log_cnf):
        logging.config.fileConfig(log_cnf['config_file'])
        Log.logger = logging.getLogger(log_cnf['default_logger'])

    def getLog(self):
        if Log.logger == None:
            Log.logger = logging.getLogger('simple')
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
