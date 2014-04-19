#coding: utf-8

import os
import json


class JsonConfiger(object):
    """JSON配置器。
    使用例子：
        configs = JsonConfiger()
        configs.load_file('/path/conf.json')
        configs.load_str('''{"foo": {"bar": "abc"}}''')
        print configs.get('foo') # return {'bar': 'abc'}
        print configs.get('foo', 'bar') # return 'abc'
        print configs.get('foo/bar') # return 'abc'
    """

    def __init__(self, encoding='utf-8'):
        self._configs = {}
        self._encoding = encoding

    def load_file(self, file_name):
        """加载文件
        """
        with open(file_name, 'r') as f:
            configs = json.load(f, encoding=self._encoding)
        includes = configs.pop('$includes', [])
        self._configs.update(configs)
        if len(includes) == 0:
            return
        dir_name = os.path.dirname(os.path.abspath(file_name))
        for i in includes:
            if i[:1] not in ['/', '\\']:
                i = os.path.join(dir_name, i)
            self.load_file(i)

    def load_str(self, str_data):
        """加载字符串
        """
        configs = json.loads(str_data, encoding=self._encoding)
        self._configs.update(configs)

    def get(self, *args):
        """获取配置内容
        """
        if not args:
            return self._configs
        is_tree_style = repr(args).find(r'/') != -1
        if is_tree_style and len(args) > 1:
            raise ValueError('args error')
        elif is_tree_style and len(args) == 1:
            params = tuple(args[0].split(r'/'))
        else:
            params = args
        d = self._configs
        for p in params:
            d = self._get(p, d)
            if not d:
                break
        return d

    def _get(self, key, d):
        return d.get(key, None)

def test():
    jsonConfig = JsonConfiger()
    jsonConfig.load_file("ice.json")
    print jsonConfig.get('nt')
    print jsonConfig.get('ice/eas_others_proxy')
    print jsonConfig.get('ice','eas_others_proxy')


if __name__ == "__main__":
    test()

