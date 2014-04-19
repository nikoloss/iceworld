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
        
    @Router.route(url=r"news/today",method=Router._GET|Router._POST)
    def test5(self,req):
        return self.cache1()

    @MemCache.lru(ttl=300)
    def cache1(self):
        ret = "暂无热点新闻"
        try:
            import urllib2
            from lxml import html as HT
            html = urllib2.urlopen("http://news.baidu.com", timeout = 10).read()
            root = HT.document_fromstring(html)
            breaking_news = root.xpath("//a[@class='a3']")
            if breaking_news:
                breaking_news = breaking_news[0].getchildren()[0].text
                ret = breaking_news
            return ret
        except Exception,e:
            raise e
