#coding: utf-8

import os, sys
import json
from abc import *
import path
import traceback


class ConfigParser(object):
    @abstractmethod
    def parseall(self, *args):
        pass


class Configer(object):
    config = {}
    setups = []

    @classmethod
    def register_my_setup(cls, *args, **deco):
        def foo(func):
            location = args[0] if args else deco.get('look')
            level = (args[1] if len(args) > 1 else deco.get('level')) or 99999
            Configer.setups.append({
                'func': func,
                'location': location,
                'level': level
            })
            return func

        return foo

    @classmethod
    def setup(cls, own_cfg):
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
