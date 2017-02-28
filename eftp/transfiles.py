# !/usr/bin/python3
# -*- coding: utf-8 -*-

# from optparse import OptionParser
from ftplib import FTP
import os
import sys
import threading
import logging
# from paramiko import SFTP

SFTP_PORT = 22
FTP_PORT = 21
lock = threading.Lock()


class TransFile:

    def __init__(
            self,
            local_path,
            remote_path,
            host,
            user,
            password,
            files=[],
            port=FTP_PORT,
            up_or_down='UP'):
        self.port = port
        self.files = files
        self.local_path = local_path
        self.remote_path = remote_path
        self.up_or_down = up_or_down
        self.__host = host
        self.__user = user
        self.__password = password
        self.Threads = []
        if sys.platform == 'win32':
            self.localSymbol = '\\'
        elif sys.platform == 'linux':
            self.localSymbol = '/'
        else:
            self.localSymbol = ''
            print(sys.platform, ' is not supported now!')
        if self.port == FTP_PORT:
            self.mftp = FTP()
        self.remoteSymbol = '/'
        # self.getReady(0)
        self.startThreads('DOWN', 10)
        self.waitThreads()

    def push_files(self):
        if self.port == FTP_PORT:
            mftp = FTP()
            mftp.set_debuglevel(1)
            try:
                mftp.connect(self.__host, FTP_PORT)
                try:
                    mftp.login(self.__user, self.__password)
                    try:
                        mftp.cwd(self.remote_path)
                        bufsize = 1024
                        for myfile in self.files:
                            if sys.platform == 'win32':
                                filename = self.local_path + '\\' + myfile
                            elif sys.platform == 'linux':
                                filename = self.local_path + '/' + myfile
                            else:
                                filename = ''
                                print(sys.platform, ' is not supported now!')
                            with open(filename, 'rb') as mfile:
                                try:
                                    remotefile = myfile.replace(
                                        self.localSymbol, self.remoteSymbol)
                                    mftp.storbinary(
                                        'STOR ' + remotefile, mfile, bufsize)
                                except Exception as e:
                                    print(
                                        'Error: Failed to upload "',
                                        filename,
                                        '" to "',
                                        self.__host,
                                        '" into "',
                                        self.remote_path,
                                        '"\nInfo: ',
                                        e)
                            print('"', filename, '" uploaded successfuly!')
                        mftp.set_debuglevel(0)
                    except Exception as e:
                        print(
                            'Error: Failed to get into the remote path "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                    finally:
                        mftp.quit()
                        print('All files are uploaded successfully!')
                except Exception as e:
                    print(
                        'Error: Failed to login "',
                        self.__host,
                        '" as "',
                        self.__user,
                        '"\nInfo: ',
                        e)
            except Exception as e:
                print(
                    'Error: Failed to connect to "',
                    self.__host,
                    '" via FTP\nInfo: ',
                    e)

    def pull_files(self):
        if self.port == FTP_PORT:
            mftp = FTP()
            mftp.set_debuglevel(2)
            if os.path.isdir(self.local_path):
                os.chdir(self.local_path)
            else:
                return 1
            try:
                mftp.connect(self.__host, FTP_PORT)
                try:
                    mftp.login(self.__user, self.__password)
                    try:
                        mftp.cwd(self.remote_path)
                        bufsize = 1024
                        for myfile in self.files:
                            localfile = myfile.replace(
                                self.remoteSymbol, self.localSymbol)
                            if sys.platform == 'win32':
                                filename = self.local_path + '\\' + localfile
                            elif sys.platform == 'linux':
                                filename = self.local_path + '/' + localfile
                            else:
                                filename = ''
                                print(sys.platform, ' is not supported now!')
                            with open(filename, 'wb') as mfile:
                                try:
                                    mftp.retrbinary(
                                        'RETR ' + myfile, mfile.write, bufsize)
                                except Exception as e:
                                    print(
                                        'Error: Failed to download "',
                                        filename,
                                        '" from "',
                                        self.__host,
                                        '" into "',
                                        self.local_path,
                                        '"\nInfo: ',
                                        e)
                            print('"', filename, '" downloaded successfuly!')
                        mftp.set_debuglevel(0)
                    except Exception as e:
                        print(
                            'Error: Failed to get into the remote path "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                    finally:
                        mftp.quit()
                        print('All files are downloaded successfully!')
                except Exception as e:
                    print(
                        'Error: Failed to login "',
                        self.__host,
                        '" as "',
                        self.__user,
                        '"\nInfo: ',
                        e)
            except Exception as e:
                print(
                    'Error: Failed to connect to "',
                    self.__host,
                    '" via FTP\nInfo: ',
                    e)

    def pu_files(self, upOrDown='UP', debugLevel=1):
        if self.port == FTP_PORT:
            mftp = FTP()
            mftp.set_debuglevel(debugLevel)
            if os.path.isdir(self.local_path):
                try:
                    os.chdir(self.local_path)
                except Exception as e:
                    print(
                        'Can not access "',
                        self.local_path,
                        '" at local\nInfo: ',
                        e)
            else:
                return 1
            try:
                mftp.connect(self.__host, FTP_PORT)
                try:
                    mftp.login(self.__user, self.__password)
                    try:
                        mftp.cwd(self.remote_path)
                        bufsize = 1024
                        for myfile in self.files:
                            if sys.platform == 'win32':
                                filename = self.local_path + '\\' + myfile
                            elif sys.platform == 'linux':
                                filename = self.local_path + '/' + myfile
                            else:
                                filename = ''
                                print(sys.platform, ' is not supported now!')
                            if upOrDown == 'DOWN':
                                localfile = myfile.replace(
                                    self.remoteSymbol, self.localSymbol)
                                with open(filename, 'wb') as mfile:
                                    try:
                                        mftp.retrbinary(
                                            'RETR ' + myfile, mfile.write, bufsize)
                                    except Exception as e:
                                        print(
                                            'Error: Failed to download "',
                                            filename,
                                            '" from "',
                                            self.__host,
                                            '" into "',
                                            self.local_path,
                                            '"\nInfo: ',
                                            e)
                                print(
                                    '"', filename, '" downloaded successfuly!')
                            elif upOrDown == 'UP':
                                with open(filename, 'rb') as mfile:
                                    try:
                                        mftp.storbinary(
                                            'STOR ' + myfile, mfile, bufsize)
                                    except Exception as e:
                                        print(
                                            'Error: Failed to upload "',
                                            filename,
                                            '" to "',
                                            self.__host,
                                            '" into "',
                                            self.remote_path,
                                            '"\nInfo: ',
                                            e)
                                print('"', filename, '" uploaded successfuly!')
                        mftp.set_debuglevel(0)
                    except Exception as e:
                        print(
                            'Error: Failed to get into the remote path "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                    finally:
                        mftp.quit()
                except Exception as e:
                    print(
                        'Error: Failed to login "',
                        self.__host,
                        '" as "',
                        self.__user,
                        '"\nInfo: ',
                        e)
            except Exception as e:
                print(
                    'Error: Failed to connect to "',
                    self.__host,
                    '" via FTP\nInfo: ',
                    e)
        return 0

    def getReady(self, debugLevel=1):
        if self.port == FTP_PORT:
            self.mftp.set_debuglevel(debugLevel)  # 默认的debug等级为1
            if os.path.isdir(self.local_path):
                try:
                    os.chdir(self.local_path)  # 进入本地的工作目录
                except Exception as e:
                    print(
                        'Can not access "',
                        self.local_path,
                        '" at local\nInfo: ',
                        e)
            else:
                return 1
            try:
                self.mftp.connect(self.__host, FTP_PORT)  # 连接服务器
                try:
                    self.mftp.login(self.__user, self.__password)  # 登录服务器
                    try:
                        self.mftp.cwd(self.remote_path)  # 进入服务器工作目录
                    except Exception as e:
                        print(
                            'Error: Failed to get into the remote path "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                except Exception as e:
                    print(
                        'Error: Failed to login "',
                        self.__host,
                        '" as "',
                        self.__user,
                        '"\nInfo: ',
                        e)
            except Exception as e:
                print(
                    'Error: Failed to connect to "',
                    self.__host,
                    '" via FTP\nInfo: ',
                    e)
        return 0

    def dispatchFiles(self, mftp, up_or_down, bufsize=1024):
        print('"', threading.current_thread().name,
              '" is calling the function of dispatchFiles')  # 打印当前线程名
        lock.acquire()  # 获取同步锁
        if len(self.files) > 0:
            myfile = self.files.pop(0)  # 文件列表首元素出栈
            file_yes_or_no = self.isfile(mftp, myfile, up_or_down)  # 判断是否是文件
            lock.release()  # 释放同步锁
        else:
            lock.release()  # 释放同步锁
            print('"', threading.current_thread().name,
                  '": No files to be transfered\n')
            return 0
        if file_yes_or_no:
            filename = self.local_path + self.localSymbol + myfile  # 获取文件全路径
            if up_or_down == 'DOWN':
                if self.localSymbol != self.remoteSymbol:
                    filename = filename.replace(
                        self.remoteSymbol, self.localSymbol)
                with open(filename, 'wb') as mfile:  # 以二进制写的方式打开文件
                    try:
                        mftp.retrbinary(
                            'RETR ' + myfile, mfile.write, bufsize)  # 下载并写入本地文件
                    except Exception as e:
                        print(
                            'Error: Failed to download "',
                            filename,
                            '" from "',
                            self.__host,
                            '" into "',
                            self.local_path,
                            '"\nInfo: ',
                            e)
                print(threading.current_thread().name, ': "',
                      filename, '" downloaded successfuly!')
            elif up_or_down == 'UP':
                with open(filename, 'rb') as mfile:  # 以二进制读的方式打开文件
                    try:
                        if self.localSymbol != self.remoteSymbol:
                            myfile = myfile.replace(
                                self.localSymbol, self.remoteSymbol)
                        mftp.storbinary(
                            'STOR ' + myfile, mfile, bufsize)  # 上传文件到远程服务器
                    except Exception as e:
                        print(
                            'Error: Failed to upload "',
                            filename,
                            '" to "',
                            self.__host,
                            '" into "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                print(threading.current_thread().name, ': "',
                      filename, '" uploaded successfuly!')
            else:
                print(up_or_down, 'must be "UP" or "DOWM"')
                return 1
        self.dispatchFiles(mftp, up_or_down)  # 递归处理文件列表的下一个元素
        # print('"', threading.current_thread().name, '" ends')  # 当前线程结束
        return 0

    def createconnection(self, port=FTP_PORT, debugLevel=0):
        if port == FTP_PORT:
            mftp = FTP()
            mftp.set_debuglevel(debugLevel)  # 默认的debug等级为0
            if os.path.isdir(self.local_path):
                try:
                    os.chdir(self.local_path)  # 进入本地的工作目录
                except Exception as e:
                    print(
                        'Can not access "',
                        self.local_path,
                        '" at local\nInfo: ',
                        e)
            else:
                return None
            try:
                mftp.connect(self.__host, FTP_PORT)  # 连接服务器
                try:
                    mftp.login(self.__user, self.__password)  # 登录服务器
                    try:
                        mftp.cwd(self.remote_path)  # 进入服务器工作目录
                    except Exception as e:
                        print(
                            'Error: Failed to get into the remote path "',
                            self.remote_path,
                            '"\nInfo: ',
                            e)
                except Exception as e:
                    print(
                        'Error: Failed to login "',
                        self.__host,
                        '" as "',
                        self.__user,
                        '"\nInfo: ',
                        e)
            except Exception as e:
                print(
                    'Error: Failed to connect to "',
                    self.__host,
                    '" via FTP\nInfo: ',
                    e)
            print('Connection established successfully!\n')
            return mftp

    def startThreads(self, up_or_down, nbrofThreads=0):
        for i in range(nbrofThreads):
            mftp = self.createconnection()
            t = threading.Thread(target=self.dispatchFiles,
                                 args=tuple([mftp, up_or_down]))
            t.start()
            self.Threads.append(t)

    def waitThreads(self):
        for t in self.Threads:
            t.join()
            # print('"', threading.current_thread().name, '" ends')  # 当前线程结束
        # self.mftp.set_debuglevel(0)
        # self.mftp.quit()

    def startTransfer(self, up_or_down, bufsize=1024):
        if len(self.files) > 0:
            myfile = self.files.pop(0)  # 文件列表首元素出栈
            if up_or_down == 'UP':
                if os.path.isdir(myfile):  # 出栈元素表示本地路径
                    newlist = os.listdir(myfile)  # 列出本地该目录下的内容
                    if newlist == []:  # 空目录
                        self.mkdir(self.mftp, 'REMOTE', myfile)  # 服务器端创建相应的空目录
                    else:
                        for i in range(len(newlist)):
                            newlist[i] = myfile + self.localSymbol + \
                                newlist[i]  # 非空目录则将路径名加到其内容列表的各元素前
                        self.files.extend(newlist)  # 新的元素列表作为新的待检内容添加到类的待检成员列表
                elif os.path.isfile(myfile):  # 出栈元素表示本地文件
                    lastindex = myfile.rfind(self.localSymbol)  # 取出路径名
                    if lastindex == -1:  # 文件在本地工作目录下
                        newdir = ''
                    else:  # 文件在本地工作目录的子目录下
                        newdir = myfile[:lastindex]
                        # 文件在本地工作目录的子目录下则先在远程创建相应的子目录
                        self.mkdir(self.mftp, 'REMOTE', newdir)
                    filename = self.local_path + self.localSymbol + myfile  # 获取本地文件全路径名
                    with open(filename, 'rb') as mfile:  # 以二进制读的方式打开文件
                        try:
                            if self.localSymbol != self.remoteSymbol:
                                myfile = myfile.replace(
                                    self.localSymbol, self.remoteSymbol)
                            self.mftp.storbinary(
                                'STOR ' + myfile, mfile, bufsize)  # 上传文件到远程服务器
                        except Exception as e:
                            print(
                                'Error: Failed to upload "',
                                filename,
                                '" to "',
                                self.__host,
                                '" into "',
                                self.remote_path +
                                self.remoteSymbol +
                                newdir,
                                '"\nInfo: ',
                                e)
                    print('"', filename, '" uploaded successfuly!')
                else:
                    print(
                        'Warning: "',
                        self.local_path +
                        self.localSymbol +
                        myfile,
                        '" does not exist')
            elif up_or_down == 'DOWN':
                try:
                    remotelist = self.mftp.nlst(myfile)  # 列出待检内容
                    if remotelist == []:
                        lastindex = myfile.rfind(
                            self.remoteSymbol)  # 查找路径分界符的最后一个索引
                        if lastindex == -1:
                            nlstpath = ''  # 待检内容在服务器工作目录下
                        else:
                            nlstpath = myfile[:lastindex]  # 待检内容在服务器工作目录的子目录下
                        try:
                            parentlist = self.mftp.nlst(
                                nlstpath)  # 列出待检内容所在目录下的内容
                            if myfile in parentlist:
                                # 待检内容在其所在的目录下，为空目录，在本地创建相应的空目录
                                self.mkdir(self.mftp, 'LOCAL', myfile)
                            else:
                                print(
                                    'Warning: "',
                                    self.remote_path +
                                    self.remoteSymbol +
                                    tocheck,
                                    '" does not exist')  # 待检内容不存
                        except Exception as e:
                            print(
                                'Error: Failed to list "',
                                self.remote_path +
                                self.remoteSymbol +
                                nlstpath,
                                '"\nInfo: ',
                                e)
                    else:
                        if [myfile] != remotelist:  # 待检内容为路径
                            try:
                                sublist = self.mftp.nlst(myfile)  # 列出路径下的内容
                                # 将路径下的内容列表添加到类的待检成员列表
                                self.files.extend(sublist)
                            except Exception as e:
                                print(
                                    'Error: Failed to list "',
                                    self.remote_path +
                                    self.remoteSymbol +
                                    myfile,
                                    '"\nInfo: ',
                                    e)
                        else:
                            lastindex = myfile.rfind(
                                self.remoteSymbol)  # 查找文件的最后一个路径分界符索引
                            if lastindex == -1:
                                newdir = ''  # 文件在服务器工作目录下
                            else:
                                newdir = myfile[:lastindex]
                                # 文件不在服务器工作目录下则先在本地创建对应的子路径
                                self.mkdir(self.mftp, 'LOCAL', newdir)
                            filename = self.local_path + self.localSymbol + \
                                myfile.replace(self.remoteSymbol, self.localSymbol)  # 本地文件的全路径
                            with open(filename, 'wb') as mfile:  # 以二进制写的方式打开文件
                                try:
                                    self.mftp.retrbinary(
                                        'RETR ' + myfile, mfile.write, bufsize)  # 下载并写入本地文件
                                except Exception as e:
                                    print(
                                        'Error: Failed to download "',
                                        filename,
                                        '" from "',
                                        self.__host,
                                        '" into "',
                                        self.local_path +
                                        self.localSymbol +
                                        newdir,
                                        '"\nInfo: ',
                                        e)
                            print('"', filename, '" downloaded successfuly!')
                except Exception as e:
                    print(
                        'Error: Failed to list "',
                        self.remote_path +
                        self.remoteSymbol +
                        myfile,
                        '"\nInfo: ',
                        e)
            self.startTransfer(up_or_down)
        else:
            print('No files to be transfered\n')
            self.mftp.set_debuglevel(0)
            self.mftp.quit()

    def mkdir(self, mftp, local_or_remote, path=''):
        if local_or_remote == 'LOCAL':
            if self.localSymbol != self.remoteSymbol:
                localpath = path.replace(
                    self.remoteSymbol, self.localSymbol)  # 替换为本地系统分界符
            if os.path.isdir(localpath) == False:
                try:
                    os.makedirs(localpath)  # 路径不存在则创建递归的路径
                except Exception as e:
                    print('Error: Failed to create directory "',
                          localpath, '" at local\nInfo: ', e)
            return True
        elif local_or_remote == 'REMOTE':
            if self.localSymbol != self.remoteSymbol:
                remotepath = path.replace(
                    self.localSymbol, self.remoteSymbol)  # 替换为远程系统分界符
            pathtree = remotepath.split(self.remoteSymbol)  # 以分界符分解路径名
            for subdir in pathtree:
                try:
                    currentlist = mftp.nlst('')  # 列出当前路径下的内容
                    if subdir not in currentlist:
                        try:
                            mftp.mkd(subdir)  # 路径名的子目录不在当前路径下则创建该子目录
                        except Exception as e:
                            print(
                                'Error: Failed to create directory "',
                                subdir,
                                '" under "',
                                self.mftp.pwd(),
                                '"\nInfo: ',
                                e)
                    try:
                        mftp.cwd(subdir)  # 创建子目录后进入子目录以创建下一层子目录
                    except Exception as e:
                        print(
                            'Error: Failed to get into "',
                            self.mftp.pwd() +
                            self.remoteSymbol +
                            subdir,
                            '"\nInfo: ',
                            e)
                except Exception as e:
                    print(
                        'Error: Failed to list current directory "',
                        self.mftp.pwd(),
                        '"\nInfo: ',
                        e)
            try:
                mftp.cwd(self.remote_path)  # 返回服务器工作目录
                return True
            except Exception as e:
                print('Error: Failed to return to the remote path\nInfo: ', e)

    def isfile(self, mftp, tocheck, up_or_down):
        if up_or_down == 'UP':
            if os.path.isdir(tocheck):  # 待检内容为路径
                newlist = os.listdir(tocheck)  # 列出路径下的内容
                if newlist == []:
                    self.mkdir(mftp, 'REMOTE', tocheck)  # 空目录则在远程服务器上创建该目录
                else:
                    for i in range(len(newlist)):
                        newlist[i] = tocheck + self.localSymbol + \
                            newlist[i]  # 非空目录则将路径名加到其内容列表的各元素前
                    self.files.extend(newlist)  # 新的元素列表作为新的待检内容添加到类的待检成员列表
                return False
            elif os.path.isfile(tocheck):
                lastindex = tocheck.rfind(self.localSymbol)  # 取出路径名
                if lastindex != -1:
                    # 文件在本地工作目录的子目录下则先在远程创建相应的子目录
                    self.mkdir(mftp, 'REMOTE', tocheck[:lastindex])
                return True
            else:
                print(
                    'Warning: "',
                    self.local_path +
                    self.localSymbol +
                    tocheck,
                    '" does not exist')
                return False
        elif up_or_down == 'DOWN':
            try:
                remotelist = mftp.nlst(tocheck)  # 列出待检内容
                if remotelist == []:
                    lastindex = tocheck.rfind(
                        self.remoteSymbol)  # 查找路径分界符的最后一个索引
                    if lastindex == -1:
                        nlstpath = ''  # 待检内容在服务器工作目录下
                    else:
                        nlstpath = tocheck[:lastindex]  # 待检内容在服务器工作目录的子目录下
                    try:
                        parentlist = mftp.nlst(nlstpath)  # 列出待检内容所在目录下的内容
                        if tocheck in parentlist:
                            # 待检内容在其所在的目录下，为空目录，在本地创建相应的空目录
                            self.mkdir(mftp, 'LOCAL', tocheck)
                        else:
                            print(
                                'Warning: "',
                                self.remote_path +
                                self.remoteSymbol +
                                tocheck,
                                '" does not exist')  # 待检内容不存在
                        return False
                    except Exception as e:
                        print(
                            'Error: Failed to list "',
                            self.remote_path +
                            self.remoteSymbol +
                            nlstpath,
                            '"\nInfo: ',
                            e)
                else:
                    if [tocheck] != remotelist:  # 待检内容为路径
                        try:
                            sublist = mftp.nlst(tocheck)  # 列出路径下的内容
                            self.files.extend(sublist)  # 将路径下的内容列表添加到类的待检成员列表
                            return False
                        except Exception as e:
                            print(
                                'Error: Failed to list "',
                                self.remote_path +
                                self.remoteSymbol +
                                tocheck,
                                '"\nInfo: ',
                                e)
                    else:
                        lastindex = tocheck.rfind(
                            self.remoteSymbol)  # 查找待检内容中的最后一个路径分界符索引
                        if lastindex != -1:
                            self.mkdir(
                                mftp, 'LOCAL', tocheck[
                                    :lastindex])  # 文件不在服务器工作目录下则先在本地创建对应的子路径
                        return True
            except Exception as e:
                print(
                    'Error: Failed to list "',
                    self.remote_path +
                    self.remoteSymbol +
                    tocheck,
                    '"\nInfo: ',
                    e)
        else:
            print('Only "UP" or "DOWN" is allowed')
            return False


def main():
    # usage='Usage: Filename [options] arg'
    # parser=OptionParser(sage)
    # parser.add_options()
    # filename=input('')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='mftp.log',
        filemode='w')
    logging.info('Start the transmission via FTP')
    mTrans = TransFile(
        'D:\\Codes\\Python',
        '/home/tangxinz',
        '135.251.238.34',
        'tangxinz',
        'zhou19891001',
        ['googletest-master'],
        21)
    # mTrans.startTransfer('DOWN')
    logging.info('Transmission complete!')

if __name__ == '__main__':
    main()
