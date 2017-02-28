# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urllib
from urllib import request
import sqlite3
import random
import threading
from bs4 import BeautifulSoup

import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

# 登录，不登录不能爬取三个月之内的数据
#import LianJiaLogIn


# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
       {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},
       {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
       {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]


# 北京区域列表
regions = [
    'dongcheng',
    'xicheng',
    'chaoyang',
    'haidian',
    'fengtai',
    'shijingshan',
    'tongzhou',
    'changping',
    'daxing',
    'yizhuangkaifaqu',
    'shunyi',
    'fangshan',
    'mentougou',
    'pinggu',
    'huairou',
    'miyun',
    'yanqing',
    'yanjiao']


lock = threading.Lock()


class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """

    def __init__(self, path, command='', *args, **kwargs):
        self.lock = threading.RLock()  # 锁
        self.path = path  # 数据库连接参数

        if command != '':
            conn = self.get_conn()
            cu = conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = sqlite3.connect(self.path)  # ,check_same_thread=False)
        conn.text_factory = str
        return conn

    def conn_close(self, conn=None):
        conn.close()

    def conn_trans(func):
        def connection(self, *args, **kwargs):
            self.lock.acquire()
            conn = self.get_conn()
            kwargs['conn'] = conn
            rs = func(self, *args, **kwargs)
            self.conn_close(conn)
            self.lock.release()
            return rs
        return connection

    @conn_trans
    def execute(self, command, method_flag=0, conn=None):
        cu = conn.cursor()
        try:
            if not method_flag:
                cu.execute(command)
            else:
                cu.execute(command[0], command[1])
            conn.commit()
        except sqlite3.IntegrityError as e:
            # print e
            return -1
        except Exception as e:
            print(e)
            return -2
        return 0

    @conn_trans
    def fetchall(self, command="select xiqou_code from xiaoqu", conn=None):
        cu = conn.cursor()
        lists = []
        try:
            cu.execute(command)
            lists = cu.fetchall()
        except Exception as e:
            print(e)
            pass
        return lists


def gen_xiaoqu_insert_command(info_dict):
    """
    生成小区数据库插入命令
    """
    info_list = [
        u'小区名称',
        u'小区代号',
        u'大区域',
        u'小区域',
        u'小区户型',
        u'建造时间',
        u'学校',
        u'地铁',
        u'均价',
        u'成交',
        u'二手房',
        u'租房']
    t = []
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t = tuple(t)
    command = (r"insert into xiaoqu values(?,?,?,?,?,?,?,?,?,?,?,?)", t)
    return command


def gen_chengjiao_insert_command(info_dict):
    """
    生成成交记录数据库插入命令
    """
    info_list = [
        u'链接',
        u'小区名称',
        u'户型',
        u'面积',
        u'朝向',
        u'楼层',
        u'年份',
        u'装修',
        u'签约时间',
        u'签约单价',
        u'签约总价',
        u'签约方',
        u'房型',
        u'交通学校等']
    t = []
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t = tuple(t)
    command = (r"insert into chengjiao values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)
    return command


def xiaoqu_spider(db_xq, url_page=u"http://bj.lianjia.com/xiaoqu/"):
    """
    爬取页面链接中的小区信息
    """
    try:
        req = request.Request(
            url_page, headers=hds[
                random.randint(
                    0, len(hds) - 1)])
        source_code = request.urlopen(req, timeout=10).read()
        # plain_text=unicode(source_code)#,errors='ignore')
        plain_text = source_code.decode()
        soup = BeautifulSoup(plain_text)
    # except (urllib.HTTPError, urllib.URLError) as e:
        # print(e)
        # exit(-1)
    except Exception as e:
        print(e)
        exit(-1)

    xiaoqu_list = soup.findAll('div', {'class': 'info-panel'})
    print('INFO: ', len(xiaoqu_list), xiaoqu_list)
    for xq in xiaoqu_list:
        print('the type is: ', type(xq))
        info_dict = {}
        info_dict.update({u'小区名称': xq.find('a').text})
        mspan = xq.find('span', {'class': 'fang-subway-ex'})
        if mspan:
            # content_subway=mspan.find('span').txt
            info_dict.update({u'地铁': mspan.find('span').text})
        mspan = xq.find('span', {'class': 'fang05-ex'})
        if mspan:
            # content_school=mspan.find('span').txt
            info_dict.update({u'学校': mspan.find('span').text})
        content = xq.find('div', {'class': 'con'}
                          ).renderContents().strip().decode()
        info = re.match(
            r".+>(.+)</a>.+>(.+)</a>.+</span>(.+)<span>.+</span>(.+)",
            content)
        if info:
            info = info.groups()
            info_dict.update({u'大区域': info[0]})
            info_dict.update({u'小区域': info[1]})
            info_dict.update({u'小区户型': info[2]})
            info_dict.update({u'建造时间': info[3][:4]})
        content_price = xq.find('div', {'class': 'price'}).find(
            'span', {'class': 'num'}).renderContents().strip().decode()
        price = re.findall('\d+(?=<)', content_price)
        if price != []:
            info_dict.update({u'均价': re.findall('\d+(?=<)', content_price)[0]})
        content_ershou = xq.find(
            'div', {
                'class': 'square'}).find(
            'span', {
                'class': 'num'}).text
        info_dict.update({u'二手房': content_ershou})
        content_chengjiao = xq.find('div', {'class': 'where'}).find('a').text
        info_dict.update({u'成交': re.findall('\d+', content_chengjiao)[1]})
        content_zufang = xq.find(
            'a', {'class': 'laisuzhou', 'href': re.compile('.*\/zf\/')}).text
        info_dict.update({u'租房': re.findall('^\d+', content_zufang)[0]})
        href_list = xq.find('a').get('href').split('/')
        if len(href_list) > 2:
            href = 'c' + href_list[2]
            info_dict.update({u'小区代号': href})
        command = gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command, 1)


def do_xiaoqu_spider(db_xq, region='changping'):
    """
    爬取大区域中的所有小区信息
    """
    url = 'http://bj.lianjia.com/xiaoqu/' + region + '/'
    try:
        req = urllib.request.Request(
            url, headers=hds[
                random.randint(
                    0, len(hds) - 1)])
        source_code = urllib.request.urlopen(req, timeout=10).read()
        plain_text = source_code.decode()
        soup = BeautifulSoup(plain_text)
    # except (urllib.HTTPError, urllib.URLError) as e:
    except Exception as e:
        print(e)
        return
    page_box = soup.find(
        'div', {
            'class': 'page-box house-lst-page-box'}).get('page-data')
    total_pages = int(re.findall('(?<="totalPage":)\d+', page_box)[0])
    print(total_pages)
    threads = []
    for i in range(total_pages):
        if i == 0:
            url_page = url
        else:
            url_page = 'http://bj.lianjia.com/xiaoqu/%s/pg%d/' % (
                region, i + 1)
        t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(u"爬下了 %s 区全部的小区信息" % region)


def chengjiao_spider(db_cj, url_page=u"http://bj.lianjia.com/chengjiao/"):
    """
    爬取页面链接中的成交记录
    """
    try:
        req = request.Request(
            url_page, headers=hds[
                random.randint(
                    0, len(hds) - 1)])
        source_code = request.urlopen(req, timeout=10).read()
        plain_text = source_code.decode()
        soup = BeautifulSoup(plain_text)
    # except (urllib.HTTPError, urllib.URLError) as e:
        # print(e)
        # exception_write('chengjiao_spider',url_page)
        # return
    except Exception as e:
        print(e)
        exception_write('chengjiao_spider', url_page)
        return

    # cj_list=soup.findAll('div',{'class':'info-panel'})
    cj_list = soup.find('ul', {'class': 'listContent'}).findAll('li')
    for cj in cj_list:
        print(cj)
        info_dict = {}
        href = cj.find('a')
        if not href:
            continue
        info_dict.update({u'链接': href.attrs['href']})
        content = cj.find('div', {'class': 'title'}).find('a').text.split()
        if len(content) > 2:
            info_dict.update({u'小区名称': content[0]})
            info_dict.update({u'户型': content[1]})
            info_dict.update({u'面积': content[2]})
        content = cj.find('div', {'class': 'houseInfo'}
                          ).renderContents().strip().decode()
        info = re.findall('(?<=span>).*(?=<)', content)
        if len(info) > 0:
            if len(info[0]) > 0:
                houseInfo = info.split('|')
                if len(houseInfo) > 1:
                    info_dict.update({u'朝向': houseInfo[0].strip()})
                    info_dict.update({u'装修': houseInfo[1].strip()})
        content = cj.find('div', {'class': 'dealDate'}).text
        if len(content) > 0:
            info_dict.update({u'签约时间': content.strip()})
        content = cj.find('div', {'class': 'totalPrice'}).find('span').text
        if len(content) > 0:
            info_dict.update({u'签约总价': content.strip()})
        content = cj.find('div', {'class': 'unitPrice'}).find('span').text
        if len(content) > 0:
            info_dict.update({u'签约单价': content.strip()})
        content = cj.find('div', {'class': 'positionInfo'}
                          ).renderContents().strip().decode()
        info = re.findall('(?<=span>).*(?=<)', content)
        if len(info) > 0:
            if len(info[0]) > 0:
                houseInfo = info.split()
                if len(houseInfo) > 1:
                    info_dict.update({u'楼层': houseInfo[0].strip()})
                    info_dict.update({u'年份': houseInfo[1].strip()[:4]})
                    info_dict.update({u'房型': houseInfo[1].strip()[6:]})
        content = cj.find('div', {'class': 'source'}).text
        if len(content) > 0:
            info_dict.update({u'签约方': content.strip()})
        content = cj.find('span', {'class': 'dealHouseTxt'}).text
        # print('ztx',content)
        # info=re.match(r'(<span>.+</span>)+',content)
        # info=info.groups()
        # print('ztx',content,info)
        info = content
        if len(info) > 0:
            # info_dict.update({u'交通学校等':','.join(info)})
            info_dict.update({u'交通学校等': info})
        command = gen_chengjiao_insert_command(info_dict)
        db_cj.execute(command, 1)


def xiaoqu_chengjiao_spider(db_cj, xq_code='c1111027378998'):
    """
    爬取小区成交记录
    """
    url = 'http://bj.lianjia.com/chengjiao/' + xq_code + "/"
    try:
        req = request.Request(
            url, headers=hds[
                random.randint(
                    0, len(hds) - 1)])
        source_code = request.urlopen(req, timeout=10).read()
        plain_text = source_code.decode()
        soup = BeautifulSoup(plain_text)
    # except (urllib.HTTPError, urllib.URLError) as e:
        # print(e)
        # exception_write('xiaoqu_chengjiao_spider',xq_name)
        # return
    except Exception as e:
        print(e)
        exception_write('xiaoqu_chengjiao_spider', xq_code)
        return
    content = soup.find('div', {'class': 'page-box house-lst-page-box'})
    total_pages = 0
    if content:
        d = content.get('page-data')
        # exec(d)
        total_pages = int(re.findall('(?<="totalPage":)\d+', d)[0])
    threads = []
    for i in range(total_pages):
        if i == 0:
            url_page = 'http://bj.lianjia.com/chengjiao/' + xq_code + '/'
        else:
            url_page = 'http://bj.lianjia.com/chengjiao/pg%d' % (
                i + 1) + xq_code + '/'
        #url_page=u"http://bj.lianjia.com/chengjiao/pg%d%s/" % (i+1,urllib.parse.quote(xq_name))
        t = threading.Thread(target=chengjiao_spider, args=(db_cj, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def do_xiaoqu_chengjiao_spider(db_xq, db_cj):
    """
    批量爬取小区成交记录
    """
    count = 0
    xq_list = db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_chengjiao_spider(db_cj, xq[0])
        count += 1
        print('have spidered %d xiaoqu' % count)
    print('done')


def exception_write(fun_name, url):
    """
    写入异常信息到日志
    """
    lock.acquire()
    f = open('log.txt', 'a')
    line = "%s %s\n" % (fun_name, url)
    f.write(line)
    f.close()
    lock.release()


def exception_read():
    """
    从日志中读取异常信息
    """
    lock.acquire()
    f = open('log.txt', 'r')
    lines = f.readlines()
    f.close()
    f = open('log.txt', 'w')
    f.truncate()
    f.close()
    lock.release()
    return lines


def exception_spider(db_cj):
    """
    重新爬取爬取异常的链接
    """
    count = 0
    excep_list = exception_read()
    while excep_list:
        for excep in excep_list:
            excep = excep.strip()
            if excep == "":
                continue
            excep_name, url = excep.split(" ", 1)
            if excep_name == "chengjiao_spider":
                chengjiao_spider(db_cj, url)
                count += 1
            elif excep_name == "xiaoqu_chengjiao_spider":
                xiaoqu_chengjiao_spider(db_cj, url)
                count += 1
            else:
                print("wrong format")
            print("have spidered %d exception url" % count)
        excep_list = exception_read()
    print('all done ^_^')


if __name__ == "__main__":
    command = "create table if not exists xiaoqu (name TEXT primary key UNIQUE, xiqou_code TEXT, regionb TEXT, regions TEXT, style TEXT, year TEXT, school TEXT, subway TEXT, price TEXT, chengjiao TEXT, ershou TEXT, zufang TEXT)"
    db_xq = SQLiteWraper('lianjia-xq.db', command)

    command = "create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, design TEXT,sign_date TEXT, unit_price TEXT, total_price TEXT,qianyuefang TEXT,fangxing TEXT, other TEXT)"
    db_cj = SQLiteWraper('lianjia-cj.db', command)

    # 爬下所有的小区信息
    # for region in regions:
    # do_xiaoqu_spider(db_xq,region)

    # 爬下所有小区里的成交信息
    do_xiaoqu_chengjiao_spider(db_xq, db_cj)

    # 重新爬取爬取异常的链接
    exception_spider(db_cj)
