#!/usr/bin/python
#coding=utf-8
# author Rowland
# edit 2014-03-19 13:58:37
import time
import datetime

class DateUtil(object):
    @staticmethod
    def get_date(fmt='%Y-%m-%d'):
        return time.strftime(fmt)
    @staticmethod
    def get_time(fmt='%H:%M:%S'):
        return time.strftime(fmt)
    @staticmethod
    def str2date(dstr, fmt='%Y-%m-%d %H:%M:%S'):
        return time.mktime(time.strptime(dstr,fmt))
    @staticmethod    
    def date2str(date, fmt='%Y-%m-%d %H:%M:%S'):
        return time.strftime(fmt, time.localtime(date))
    @staticmethod
    def current():
        return time.time()

    @staticmethod
    def diff_time(begin,end):
        '''
            type datetime
            begin,end format yyyy-MM-dd HH:mm:ss or datetime
            return seconds
        '''
        date1 = None
        date2 = None
        if type(begin) is str or isinstance(begin, unicode):
            date1 = datetime.datetime.strptime(begin,'%Y-%m-%d %H:%M:%S') #%Y-%d-%m %H:%M:%S
        elif type(begin) is datetime.datetime:
            date1 = begin
        else:
            raise ValueError,'begin invalid argument'

        if type(end) is str or isinstance(end, unicode):
            date2 = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M:%S')
        elif type(end) is datetime.datetime:
            date2 = end
        else:
            raise ValueError,'endtime argument error'
        td = date2 - date1 # return datedelta obj
        total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        return total_seconds #diff.total_seconds()

    @staticmethod
    def add_day(nday=0, isql=True):
        '''
            n can nav
        '''
        now = datetime.datetime.now()
        aday = datetime.timedelta(days=nday)
        now += aday
        if isql:
            return datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
        return now

    @staticmethod
    def add_day_night(nday=0, isstr=True):
        ''' 凌晨时间
            n can nav
        '''
        now = datetime.datetime.now()
        aday = datetime.timedelta(days=nday)
        now += aday
        time_str = datetime.datetime.strftime(now, '%Y-%m-%d ')+"00:00:00"
        if isstr:
            return time_str
        return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')


    @staticmethod
    def is_between(begintime, endtime, opttime=None):
        ''' opttime 是否在 begintime , endtime 之间, 默认为当前时间
            @param begintime : datatime.datetime or time_str
        '''
        if not opttime:
            opttime = datetime.datetime.now()
        elif isinstance(opttime, str):
            try:
                opttime = datetime.datetime.strptime(opttime, '%Y-%m-%d %H:%M:%S')
            except:
                opttime = datetime.datetime.strptime(opttime, '%Y-%m-%d')
        elif isinstance(opttime, datetime.datetime):
            pass
        else:
            raise ValueError('opttime args err')

        if isinstance(begintime, str):
            try:
                begintime = datetime.datetime.strptime(begintime,'%Y-%m-%d %H:%M:%S')
            except:
                begintime = datetime.datetime.strptime(begintime,'%Y-%m-%d')
        elif isinstance(begintime, datetime.datetime):
            pass
        else:
            raise ValueError("begintime args err")

        if isinstance(endtime, str):
            try:
                endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
            except:
                endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
        elif isinstance(endtime, datetime.datetime):
            pass
        else:
            raise ValueError("endtime args err")

        if DateUtil.diff_time(opttime, begintime) < 0 and DateUtil.diff_time(opttime, endtime) >=0 :
            return True
        else:
            return False

if __name__ == "__main__":
    print DateUtil.get_date()
    print DateUtil.get_time()
    print DateUtil.str2date("2014-09-08 11:09:12")
    cur = DateUtil.current()
    print cur,DateUtil.date2str(cur)
    print DateUtil.diff_time("2013-03-01 12:00:00","2013-03-01 12:00:05")

    print DateUtil.add_day(-3)
    print DateUtil.add_day_night(-3)

    print DateUtil.is_between('2014-03-31 12:10:00', '2014-03-31')
    print DateUtil.is_between('2014-03-31', '2014-03-31 13:10:00')
    print DateUtil.is_between('2014-03-31', '2014-03-31 13:10:00', opttime='2014-03-31 12:14:00')
