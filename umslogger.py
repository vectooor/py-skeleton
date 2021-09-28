#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: jcouyang
# date: 2021-01-06

import datetime
import logging
import logging.handlers
import os

'''
日志模块
'''
today = datetime.datetime.now().strftime("%Y%m%d")
LOG_FILENAME = 'logs/ums_{}.log'.format(today)
if not os.path.exists(os.path.dirname(LOG_FILENAME)):
    os.makedirs(os.path.dirname(LOG_FILENAME))

logger = logging.getLogger()

def set_logger():
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-[%(process)d-%(threadName)s]-'
                                  '[%(pathname)s line:%(lineno)d]-%(levelname)s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

set_logger()
