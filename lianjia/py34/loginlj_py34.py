# -*- coding: utf-8 -*-
import urllib
from http.cookiejar import CookieJar
#import urllib2
import json
import time
import re
import io
#获取Cookiejar对象（存在本机的cookie消息）
cookie = CookieJar()
#自定义opener,并将opener跟CookieJar对象绑定
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
#安装opener,此后调用urlopen()时都会使用安装过的opener对象
urllib.request.install_opener(opener)
 
#home_url = 'http://bj.lianjia.com/'
home_url ='http://bj.lianjia.com/?ticket=ST-3472563-UJn2VqMDq6Bw1ZKD7rNu-www.lianjia.com'
auth_url = 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F'
#auth_url ='https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F&renew=1'
chengjiao_url = 'http://bj.lianjia.com/chengjiao/'
 
 
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}
# 获取lianjia_uuid
req = urllib.request.Request(home_url)
opener.open(req)
#print('txzhou',opener.open(req).read().decode())
print('INFO: COOKIE is: ',cookie)
# 初始化表单
req = urllib.request.Request(auth_url, headers=headers)
#print('txzhou',req)
result = opener.open(req)
print('INFO: COOKIE is: ',cookie)
#print('txzhou result',result.getheaders())
#print('txzhou',result.read())
# 获取cookie和lt值
pattern = re.compile(r'JSESSIONID=(.*)')
jsessionid = pattern.findall(result.getheader('Set-Cookie').split(';')[0])[0]
print('INFO: JSESSIONID is: ',jsessionid)
if result.getheader('Content-Encoding')=='gzip':
    import gzip
    buf = io.BytesIO(result.read())
    f = gzip.GzipFile(fileobj=buf)
    html_content = f.read().decode()
#html_content = result.read().decode('GB2312','ignore')
#print('txzhou',type(html_content))
#print('txzhou',html_content)
pattern = re.compile(r'value=\"(LT-.*)\"')
lt = pattern.findall(html_content)[0]
print('INFO: LT is: ',lt)
pattern = re.compile(r'name="execution" value="(.*)"')
execution = pattern.findall(html_content)[0]
print('INFO: EXECUTION is: ',execution)
# print(cookie)
# opener.open(lj_uuid_url)
# print(cookie)
# opener.open(api_url)
# print(cookie)
 
# data
data = {
    'username': '15000573643',
    'password': 'zhou19891001',
    # 'service': 'http://bj.lianjia.com/',
    # 'isajax': 'true',
    # 'remember': 1,
    'execution': execution,
    '_eventId': 'submit',
    'lt': lt,
    'verifyCode': '',
    'redirect': '',
}
# urllib进行编码
post_data=urllib.parse.urlencode(data).encode()
#print('INFO: ',post_data)
# header
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Content-Length': '152',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Origin': 'https://passport.lianjia.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'X-Requested-With': 'XMLHttpRequest',
}
 
headers2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'bj.lianjia.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport.lianjia.com/cas/xd/api?name=passport-lianjia-com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}
req = urllib.request.Request(auth_url, post_data, headers)
try:
    print('INFO: COOKIE is: ',cookie)
    result = opener.open(req)
except urllib.error.HTTPError as e:
    print('INFO: ',e.getcode())
    print('INFO: ',e.reason)
    print('INFO: ',e.geturl()) 
    print("-------------------------")
    print('INFO: ',e.info())
    print('INFO: ',e.geturl())
    req = urllib.request.Request(e.geturl())
    result = opener.open(req)
    req = urllib.request.Request(chengjiao_url)
    result = opener.open(req).read()
    #print(result)
