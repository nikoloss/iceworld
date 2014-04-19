#!/usr/bin/python
#coding=utf-8
#author Rowland
#edit 2014-03-19 14:15:54
import os, sys

_HOME_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
_BIN_PATH = os.path.join(_HOME_PATH, 'bin')
_BIZ_PATH = os.path.join(_HOME_PATH, 'biz')
_ETC_PATH = os.path.join(_HOME_PATH, 'etc')

_path =()
_path += _BIN_PATH, _BIZ_PATH, _ETC_PATH
map(sys.path.append, _path)

