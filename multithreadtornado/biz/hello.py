#encoding=utf-8

import time
from util.route import Router
from util.cache import MemCache

class HelloTest(object):
    
    @Router.route(url=r"hello/([a-z]+)",method=Router._GET|Router._POST)
    def test(self,req,who):
        #http://localhost:8888/hello/billy
        return "Hi,"+who
        
    @Router.route(url=r"greetings/([a-z]+)",method=Router._GET)
    def test2(self,req,who):
        #http://localhost:8888/greetings/rowland
        raise Exception("error")

    @Router.route(url=r"book/([a-z]+)/(\d+)",method=Router._GET|Router._POST)
    def test3(self,req,categories,bookid):
        #http://localhost:8888/book/medicine/49875
        return "You are looking for a "+categories+" book\n"+"book No. " + bookid
        
    @Router.route(url=r"json",method=Router._GET|Router._POST)
    def test4(self,req):
        #http://localhost:8888/json
        #print req.request.body
        who=req.json_args.get("who","default")
        age=req.json_args.get("age",0)
        person={}
        person['who']=who
        person['age']=int(age)
        return person
