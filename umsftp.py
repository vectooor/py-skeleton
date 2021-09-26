#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: jcouyang
# date: 2018-11-28

"""
上传和下载FTP文件进行简单封装
"""

import datetime
import os
import sys 
import ftplib

from umsconfig import globalConfig
from umslogger import logger

def ftp_connect(ftp_config):
    """建立FTP链接
    
    Args:
        host: 主机IP
        port: 主机端口
        username: 用户名
        password: 密码

    Returns:
        A ftp connection handler

    """

    host = ftp_config['host']
    port = int(ftp_config['port'])
    username = ftp_config['username']
    password = ftp_config['password']

    # 创建ftp对象实例 
    ftp = ftplib.FTP()
    # 打开调试级别2，显示详细信息
    ftp.set_debuglevel(2)
    ftp.connect(host, port, timeout=30)
    # 登录，如果匿名登录则用空串代替即可
    ftp.login(username, password)
    return ftp

def download(ftp, local, remote):
    """下载远程FTP文件到本地

    Args:
        local:  本地文件的绝对路径
        remote: 远程文件的绝对路径

    Returns:
        void

    """

    # 设置缓冲块大小
    bufSize = 2048
    # 以写模式在本地打开文件
    fp = open(local, 'wb')
    # 接收服务器上文件并写入本地文件
    command = 'RETR {}'.format(remote)
    logger.info('下载文件执行的命令=[{}]'.format(command))
    ftp.retrbinary(command, fp.write, bufSize)
    # 关闭调试
    ftp.set_debuglevel(0)
    fp.close()
    # 退出ftp服务器
    ftp.quit()

def upload(ftp, local, remote):
    """上传本地文件到远程FTP目录
    
    Args:
        local:  本地文件的绝对路径
        remote: 远程文件的绝对路径

    Returns:
        void

    """

    #设置缓冲块大小
    bufSize = 2048
    fp = open(local, 'rb')
    #try:
    #    today = datetime.datetime.now().strftime("%Y%m%d")
    #    ftp.mkd(today)
    #except:
    #    print ("文件存在，无需再创建")
    #上传文件
    command = 'STOR {}'.format(remote)
    logger.info('上传文件执行的命令=[{}]'.format(command))
    ftp.storbinary(command, fp, bufSize)
    #关闭调试
    ftp.set_debuglevel(0)
    fp.close()
    ftp.quit()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Useage:%s date' % (sys.argv[0]))
        print('\tdate\t- 交易日期，格式YYYYMMDD')
        exit()

    ftp_config = {}
    ftp_config['host'] = globalConfig.get('FTP', 'ftp.host')
    ftp_config['port'] = globalConfig.get('FTP', 'ftp.port')
    ftp_config['username'] = globalConfig.get('FTP', 'ftp.username')
    ftp_config['password'] = globalConfig.get('FTP', 'ftp.password')

    home = os.path.expanduser("~")
    date = sys.argv[1]

    # 交易文件
    remote = '/atest.txt'
    local  = '{}/a_{}.txt'.format(home, date)
    ftp = ftp_connect(ftp_config)
    download(ftp, local, remote)

