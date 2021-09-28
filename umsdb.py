#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: jcouyang
# date: 2018-12-22

"""
基于mysql.connector进行简单封装
"""

import json
import mysql.connector
import traceback

from umslogger import logger
from umsexception import UmsException

class UmsDB(object):
    sql    = ''
    conn   = None
    cursor = None

    def __init__(self, host, port, username, password, database,
                charset='utf8', table_prefix='', raise_on_warnings=True):
        '''构造函数

        Args:
            @param host              : 数据库的地址，IP
            @param port              : 端口
            @param username          : 用户
            @param password          : 密码
            @param database          : 数据名
            @param charset           : 字符编码
            @param table_prefix      : 数表的前缀
            @param raise_on_warnings : 是否显示警告

        Returns: void
        '''
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = int(port)
        self.charset = charset
        self.table_prefix = table_prefix
        self.raise_on_warnings = bool(raise_on_warnings)

    def connect(self, force=False):
        if self.conn is None or force is True:
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    raise_on_warnings=self.raise_on_warnings)

                self.cursor = self.conn.cursor(dictionary=True, buffered=True)
                if self.charset is not None:
                    # 字符串一行太长写不下
                    # 通过括号进行连接，每行字符串都由引号引起来
                    self.executeSQL(("SET "
                                "character_set_connection='{}', "
                                "character_set_results='{}', "
                                "character_set_client=binary").format(self.charset, self.charset))
            except Exception as err:
                logger.error("connection error: {}".format(traceback.format_exc()))
                raise UmsException("connection error")

        return self.conn

    def findOneEx(self, table='', where=None, field=None, order=None, sql=None):
        '''查找一条记录，返回的是一个对象，对findOne的一个优化

        Args:
            @param table     : 表名
            @param where     : 查询条件
            @param field     : 要查询的列
            @param password  : 密码
            @param order     : 排序，例：ORDER BY create_time DESC
            @param sql       : 完整的SQL，前面的where、field、order均不在生效

        Returns: object
        '''
        result = self.findOne(table, where, field, order, sql)
        if len(result) <= 0:
            logger.warn('result is empty')
            return None
        
        # 有数据，选取第一个
        return result[0]

    def findOne(self, table='', where=None, field=None, order=None, sql=None):
        '''查找一条记录，这里返回的仍然是一个数组，且使用时需判断数组是否为空

        Args:
            @param table     : 表名
            @param where     : 查询条件
            @param field     : 要查询的列
            @param password  : 密码
            @param order     : 排序，例：ORDER BY create_time DESC
            @param sql       : 完整的SQL，前面的where、field、order均不在生效

        Returns: list
        '''
        return self._find(table, where, field, order, 1, sql)

    def findList(self, table='', where=None, field=None, order=None, limit=None, sql=None):
        '''查找多条记录

        Args:
            @param table     : 表名
            @param where     : 查询条件
            @param field     : 要查询的列
            @param password  : 密码
            @param order     : 排序，例：ORDER BY create_time DESC
            @param limit     : 本次最多查询多少条
            @param sql       : 完整的SQL，前面的where、field、order均不在生效

        Returns:
        '''
        return self._find(table, where, field, order, limit, sql)

    def _find(self, table='', where=None, field=None, order=None, limit=1, sql=None):
        '''内部调用函数

        Args:
            @param table     : 表名
            @param where     : 查询条件
            @param field     : 要查询的列
            @param password  : 密码
            @param order     : 排序，例：ORDER BY create_time DESC
            @param sql       : 完整的SQL，前面的where、field、order均不在生效

        Returns:
        '''
        if not sql:
            # 等价于其他语言的三目运算符
            # where = where == null ? '1=1' : where
            where = where if where else '1=1'
            field = field if field else '*'
            order = order if order else ''
            limit = ('limit %s' % str(limit)) if limit else ''

            if type(field) == list:
                field = '`%s`' % ("`,`".join(field))
            sql = "SELECT %s FROM %s WHERE %s %s %s" % (field, self.table(table), where, order, limit)
        self.executeSQL(sql)

        # fetchone返回的是一个dict，上面的findOneEx会有问题
        # 解决方案可以调整findOne，也可以调整这里 2021-09-28
        # if 1 == limit:
        #     return self.cursor.fetchone()
        # else:
        #     return self.cursor.fetchall()

        return self.cursor.fetchall()


    def insertSelective(self, table, params):
        '''插入，去除值为空的字段

        Args:
            @param table     : 表名
            @param params    : 插入的数据

        Returns: 本次插入的自增Id值
        '''
        return self.insert(table, params, True)

    def insert(self, table, params, selective=False):
        '''插入

        Args:
            @param table     : 表名
            @param params    : 插入的数据，建议dict类型
            @param selective : 是否去除值为空的字段

        Returns: 本次插入的自增Id值
        '''
        field = []

        t = type(params)
        if t == dict:
            if selective: 
                params = dict((k,v) for k,v in params.items() if v)
            field = list(params.keys())
        elif t == list:
            field = params[0]
            if not isinstance(field, dict):
                raise UmsException("error params,need list[dict]")
            field = list(field.keys())
        else:
            raise UmsException("error params,need dict")

        if not field or not isinstance(field, list):
            raise UmsException("error params,need dict")
        
        values = '%({})s'.format(")s,%(".join(field))
        field = '`%s`' % "`,`".join(field)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (self.table(table), field, values)
        
        self.executeSQL(sql, params)
        self.conn.commit()

        return self.cursor.lastrowid


    def insertBatchEx(self, table, data):
        """ 批量插入数据，当数据较多时，单条插入会非常耗时
            这里需要手动的开启事务

        Args:
            table: 表名
            data:  要写入数据库的数据，这里是一个数组格式
                   数组内部是一个字典类型，key为数据库字段名，value为值

        Returns: 影响的行数
        """

        t = type(data)
        if t != list:
            raise UmsException("error data,need list[list]")

        cols = []
        vals = []
        for item in data:
            if type(item) != dict:
                raise UmsException("error data element,need list[list]")

            if not cols:
                cols = list(item.keys())

            vals.append(list(item.values()))
        
        return self.insertBatch(table, cols, vals, auto_commit=False)


    def insertBatch(self, table, cols, vals, auto_commit=True):
        """批量插入数据，当数据较多时，单条插入会非常耗时

        Args:
            table: 表名
            cols: 表列，数组
            vals: 每列对应的值，数组，数组的元素还是一个数组
            auto_commit: 事务是否自动提交，一般而言，分批插入可能会自己启动事务

        Returns: 影响的行数
        """
        
        t = type(cols)
        if t != list:
            raise UmsException("error cols,need list[list]")

        t = type(vals)
        if t != list:
            raise UmsException("error vals,need list[list]")

        field = '`%s`' % "`,`".join(cols)

        placeholder = "(%s"
        for i in range(len(cols) - 1):
             placeholder += ",%s"
        placeholder += ")"
        
        sql = "INSERT INTO %s (%s) VALUES %s" % (self.table(table), field, placeholder)
        self.executeSQL(sql, vals)
        if auto_commit:
            self.conn.commit()

        return self.cursor.rowcount


    def updateSelective(self, table, where, params):
        """条件更新表，去除字典中值为空的字段

        Args:
            @param table     : 表名
            @param where     : 更新条件
            @param params    : 要更新的字段和值，dict结构

        Returns: 影响的行数
        """
        return self.update(table, where, params, True)

    def update(self, table, where, params, selective=False):
        """条件更新表

        Args:
            @param table     : 表名
            @param where     : 更新条件，为空则更新全部
            @param params    : 要更新的字段和值，dict结构
            @param selective : 是否去除值为空的字段

        Returns: 影响的行数
        """
        field = []
        t = type(params)
        if t == dict:
            if selective:
                params = dict((k,v) for k,v in params.items() if v)
            field = list(params.keys())
        elif t == list:
            field = params[0]
            if not isinstance(field, dict):
                raise UmsException("error params,need list[dict]")
            field = list(field.keys())
        else:
            raise UmsException("error params,need dict")

        if not field or not isinstance(field, list):
            raise UmsException("error params,need dict")

        # where为空则更新全部
        where = where if where else '1=1'

        t = []
        for item in field:
            t.append('`{}`=%({})s'.format(item, item))

        sql = "UPDATE %s SET %s WHERE %s" % (self.table(table), ",".join(t), where)
        self.executeSQL(sql, params)
        self.conn.commit()

        # 影响的行数
        # 实践证明：如果传入的参数值和数据库的值一致，这里会返回0
        return self.cursor.rowcount

    def count(self, table='', where=None, sql=None):
        '''根据条件或指定的SQL统计数据的条数

        Args:
            @param table     : 表名
            @param where     : 查询条件
            @param sql       : 完整的SQL，前面的where、field、order均不在生效

        Returns: 条数
        '''
        count = 0
        if not sql:
            where = where if where else '1=1'
            sql = "SELECT COUNT(*) AS NUM FROM %s WHERE %s" % (self.table(table), where)
        self.executeSQL(sql)

        rs = self.cursor.fetchone()
        if rs is not None:
            count = rs['NUM']
        return count

    def executeSQL(self, sql, params=None):
        self.sql = sql
        logger.debug('execute sql=[{}]'.format(sql))

        if params:
            dump = json.dumps(params, ensure_ascii=False)
            logger.debug('params=[{}]'.format(dump))
            t = type(params)
            if t == dict:
                return self.cursor.execute(sql, params)
            elif t == list:
                return self.cursor.executemany(sql, params)
            else:
                raise UmsException("illegal parameter type")

        return self.cursor.execute(sql, params)


    def delete(self, table, where):
        """删除，where为空则删除全部

        Returns: 删除了多少条记录
        """
        where = where if where else '1=1'
        sql = "DELETE FROM %s WHERE %s" % (self.table(table), where)
        self.executeSQL(sql)
        self.conn.commit()
        return self.cursor.rowcount

    def table(self, table):
        """可以增加前缀等操作
        """
        return table

    def getSQL(self):
        """获取当前在执行的SQL
        """
        return self.sql

    def close(self):
        """关闭连接
        """
        self.cursor.close()
        self.conn.close()
        logger.info("connection closed")

    def startTrans(self):
        """开启事务
        """
        self.conn.start_transaction()

    def commit(self):
        """提交事务
        """
        self.conn.commit()
        logger.info("trasaction commited")

    def rollback(self):
        """回退事务
        """
        self.conn.rollback()
        logger.info("trasaction rollback")


if __name__ == '__main__':

    from umsconfig import globalConfig
    host = globalConfig.get('DATABASE', 'db.host')
    port = globalConfig.get('DATABASE', 'db.port')
    username = globalConfig.get('DATABASE', 'db.username')
    password = globalConfig.get('DATABASE', 'db.password')
    database = globalConfig.get('DATABASE', 'db.database')

    logger.info("host=[{}],port=[{}],username=[{}],password=[{}],database=[{}]"
                .format(host, port, username, password, database))

    db = UmsDB(host, port, username, password, database)
    db.connect()

    result = db.findList('t_test', field=['message'], where='id = 1')
    logger.info(db.getSQL())
    logger.info(result)

    # 插入数据
    result = db.insertSelective('t_test', {'title':'title', 'message': 'message'})
    logger.info(db.getSQL())
    logger.info(result)

    result = db.insertBatch('t_test', ['title', 'message'],
                            [['title1', '中文'],
                            ['title2', 'message2']])
    logger.info(db.getSQL())
    logger.info(result)

    # 更新数据
    result = db.updateSelective('t_test', 'id=9', {'title':'哈喽哈喽', 'message': '更新'})
    logger.info(db.getSQL())
    logger.info(result)

    result = db.delete('t_test', 'id>=20')
    logger.info(db.getSQL())
    logger.info(result)

    result = db.count('t_test')
    logger.info(db.getSQL())
    logger.info(result)

    db.close()
