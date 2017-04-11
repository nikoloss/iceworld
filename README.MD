ICEworld
=========
A multithread implementation based on Tornado

###### a fast restful dev framework based on tornado.

###### Take advantage of a fashionable C10K framework Tornado(ioloop).

###### ioloop throws requests to threadpool, threadpool notifies ioloop when it is done.

###### Before deployment, `tornado` and `futures` are required.
```bash
    sudo easy_install tornado
    sudo easy_install futures
    sudo easy_install lxml
```
#### Quick Start
1.在“biz”目录中创建一个py文件，文件名任意但最好不要跟第三方库冲突

2.使用 "Router.route" 装饰器注册函数到路由表中，仿造示例即可

3.到“bin”目录下，使用命令"python serv.py" 启动工程，用浏览器访问步骤二中注册的路径可看到效果


基于tornado改装的多线程业务处理模型框架，自带跨域请求，json/xml参数解析，缓存和路由优化。适合多人合作的service系统后台搭建！
>疑问请联系:
<rowland.lan@163.com>

***no rights reserved, enjoy!!***
