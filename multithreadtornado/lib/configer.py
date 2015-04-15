#coding: utf-8

import os, sys
import json
from abc import *
import path
import traceback


class ConfigParser(object):
    '''
        This abstract class provides a strategy of how to get those configurations
        through a file or remote config ?
    '''
    @abstractmethod
    def parseall(self, *args):
        pass


class E(object):
    def __init__(self, func):
        self.func = func

    def __ror__(self, inputs):
        return self.func(inputs)


class Configer(object):
    '''
        This class will hold configurations and registered setups(functions)
        It can determine when to setup them
    '''
    config = {}
    setups = []

    @classmethod
    def register_my_setup(cls, **deco):
        def foo(func):
            location = deco.get('look')
            level = deco.get('level', 99999)
            Configer.setups.append({
                'func': func,
                'location': location,
                'level': level
            })
            return func

        return foo

    @classmethod
    def setup(cls, own_cfg, onlevel=0):
        '''
            Call all(or specific level) setup functions which registered via using
            "Configer.register_my_setup" decorator.
            If "onlevel" has been set, only the matched setup fucntions will be
            loaded(or hot reloaded).
            BE CAREFUL! The registed setup function shall apply reload logic in case
            of a runtime-hot-reloaded callback hit.
        '''
        Configer.setups.sort(key=lambda x: x['level'])
        Configer.config.update(own_cfg)
        #automic scan dirs
        files_list = os.listdir(path._LIB_PATH)
        files_list = set([x[:x.rfind(".")] for x in files_list if x.endswith(".py")])
        map(__import__, files_list)
        for s in Configer.setups:
            func = s['func']
            location = s['location']
            try:
                if location:
                    func(Configer.config[location])
                else:
                    func()
            except Exception:
                traceback.print_exc()
                sys.exit(1)


class ConfigParserFromFile(ConfigParser):
    '''
        via Config Files
    '''
    def parseall(self, fullpath):
        etc = path._ETC_PATH
        cfg = {}
        with open(fullpath, 'r') as f:
            cfg = json.loads(f.read())
        if cfg.get('$includes'):
            for include in cfg['$includes']:
                icfg = self.parseall(os.path.join(etc, include))
                cfg.update(icfg)
        return cfg
