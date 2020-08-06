# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import os
import sqlite3
import pymysql
import logging
import configparser
import libs.core as Core
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB

log = logging.getLogger(__name__)

class Config(object):
    def __init__(self):
        db_conf_path =  Core.db_conf_file
        self.cf = configparser.ConfigParser()
        self.cf.read(db_conf_path)

    def get_sections(self):
        return self.cf.sections()

    def get_options(self,section):
        return self.cf.options(section)

    def get_content(self,section):
        result = {}
        for option in self.get_options(section):
            value =self.cf.get(section,option)
            result[option] =  int(value) if value.isdigit() else value
        return result

# 数据池
class DataPool():
    # 连接池对象
    __pool__ = None

    # 初始化构造函数，默认使用mysql的配置信息
    def __init__(self, conf_name=None, dbName=None, db_out_dir=None):
        self.conf_name = conf_name
        # 获取配置文件中的配置信息
        if conf_name is None:
            log.info("use mysql")
            self.conf = Config().get_content("MySQL")
            # 数据库构造函数，从链接池中取出连接，并生成操作游标
            self.__get_mysql_conn_pool__(**self.conf)
        else:
            log.info("use sqllite")
            self.conf = Config().get_content(conf_name)
            if db_out_dir:
                self.conf["db_out_dir"] =  db_out_dir
            self.__get_sqlite_conn_pool__(dbName,**self.conf)

    # 设置Mysql数据池的信息
    def __get_mysql_conn_pool__(self,host,port,user,password,db_name=None):
        self.__pool__ = PooledDB(creator=pymysql, # 使用链接数据库的模块
                        mincached=1, # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                        maxconnections=0, # 链接池允许的最大链接数，0和None表示不限制连接数
                        maxcached=20, # 链接池中最多闲置的链接，0和None标识不限制
                        host=host,
                        port=port,
                        user=user,
                        passwd=password,
                        db=db_name,
                        use_unicode=False,
                        charset="utf8",
                        cursorclass=DictCursor)

    # 设置sqlite数据库信息
    def __get_sqlite_conn_pool__(self,dbName,db_out_dir):
        try:
            dbFile = os.path.join(db_out_dir,str(dbName)+".db")
            log.info("dbFilePath:"+str(dbFile))
            self.__pool__ = PersistentDB(sqlite3,maxusage=10,database=dbFile)
            if not os.path.exists(dbFile):
                self.__create_sqlite_tables__()
        except Exception as e:
            log.exception(e)

    def create_tables(self,sql):
        '''
        @summary: 创建表
        @param dbFile: sqlite数据库文件路径
        @param sql: 创建数据表的sql语句
        '''
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        self.__close__(cursor,conn)
        log.info("table create success!")

    def drop_tables(self,sql):
        '''
        @summary: 删除表
        @param dbFile: sqlite数据库文件路径
        @param sql: 删除数据表的sql语句
        '''
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        self.__close__(cursor,conn)
        log.info("table drop success!")


    def getAll(self,sql,param=None):
        '''
            @summary: 执行查询，并取出所有结果集
            @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
            @param param: 可选参数，条件列表值（元组/列表）
            @return: result list(字典对象)/boolean 查询到的结果集
        '''
        return  self.action(0,sql,param)


    def getOne(self,sql,param=None):
        '''
            @summary: 执行查询，并取出第一条
            @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
            @param param: 可选参数，条件列表值（元组/列表）
            @return: result list/boolean 查询到的结果集
        '''
        return  self.action(1,sql,param)


    def getMany(self,sql,num, param=None):
        '''
            @summary: 执行查询，并取出num条结果
            @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
            @param num:取得的结果条数
            @param param: 可选参数，条件列表值（元组/列表）
            @return: result list/boolean 查询到的结果集
        '''
        return self.action(2,sql,param,num)

    def insertMany(self,sql,param=None):
        '''
            @summary: 向数据表插入多条记录
            @param sql:要插入的ＳＱＬ格式
            @param param:要插入的记录数据tuple(tuple)/list[list]
            @return: result 受影响的行数
        '''
        return self.action(3,sql,param)


    def update(self,sql,param=None):
        '''
            @summary: 更新数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要更新的  值 tuple/list
            @return: result 受影响的行数
        '''
        return self.action(4,sql,param)


    def insert(self,sql,param=None):
        '''
            @summary: 更新数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要更新的  值 tuple/list
            @return: result 受影响的行数
        '''
        return self.action(5,sql,param)

    def delete(self,sql,param=None):
        '''
            @summary: 删除数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要删除的条件 值 tuple/list
            @return: result 受影响的行数
        '''
        return self.action(6,sql,param)


    def action(self, type, sql, param, num=None):
        '''
            @summary: 数据库方法操作集合
            @param type: 用于执行各种操作的占位符
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 需要执行的条件 值 tuple/list
            @return: result list/boolean 查询到的结果集
        '''
        log.info("Action Flag is:"+str(type))
        log.info(sql)
        result = False
        if self.conf_name is None:
            result =  self.mysql_action(type, sql, param, num)
        else:
            result = self.sqlite_action(type, sql, param, num)
        return result

    # mysql数据库操作
    def mysql_action(self,type, sql, param, num=None):
        '''
            @summary: 数据库方法操作集合
            @param type: 用于执行各种操作的占位符
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 需要执行的条件 值 tuple/list
            @return: result list/boolean 查询到的结果集
        '''
        result = False
        con = None
        cur = None
        try:
            con = self.__pool__.connection()
            cur = con.cursor()

            if param is None:
                if not(type == 3):
                    count = cur.execute(sql)
                else:
                    count = cur.executemany(sql)
            else:
                if not(type == 3):
                    count = cur.execute(sql,param)
                else:
                    count = cur.executemany(sql,param)

            if count > 0:
                # 查询所有的数据
                if type == 0:
                    result = cur.fetchall()
                # 查询单条数据
                elif type == 1:
                    result = cur.fetchone()
                # 查询指定条数的数据
                elif type == 2:
                    if not (num is None):
                        result = cur.fetchmany(num)
                # 从数据库中 增加/删除/更新数据
                else:
                    result = count
                    con.commit()
        except Exception as e:
            if type>= 3:
                con.rollback() # 事务回滚
            log.exception(e)
        finally:
            self.__close__(cur,con)
        return result

    # sqlite 数据库操作
    def sqlite_action(self,type, sql, param, num=None):
        '''
            @summary: 数据库方法操作集合
            @param type: 用于执行各种操作的占位符
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 需要执行的条件 值 tuple/list
            @return: result list/boolean 查询到的结果集
        '''
        result = False
        con = None
        cur = None
        try:
            con = self.__pool__.connection()
            cur = con.cursor()

            if param is None:
                if not(type == 3):
                    object = cur.execute(sql)
                else:
                    object = cur.executemany(sql)
            else:
                if not(type == 3):
                    object = cur.execute(sql,param)
                else:
                    object = cur.executemany(sql,param)

            count = object.rowcount
            if count == -1:
                # 查询所有的数据
                if type == 0:
                    result = cur.fetchall()
                # 查询单条数据
                elif type == 1:
                    result = cur.fetchone()
                # 查询指定条数的数据
                elif type == 2:
                    if not (num is None):
                        result = cur.fetchmany(num)

            # 从数据库中 增加/删除/更新数据
            elif count>0:
                result = count
                con.commit()
            
            
        except Exception as e:
            if type>= 3:
                con.rollback() # 事务回滚
            log.exception(e)
        finally:
            self.__close__(cur,con)

        return result
    
    def __create_sqlite_tables__(self):
        '''
            @summary: 微信公众号信息表
            @param id: 唯一自增ID值
            @param fakeid: 公众号的id
            @param alias: 公众号的微信号
            @param nickname: 公众号名称
        '''
        wechat_info =  '''CREATE TABLE "wechat_info"("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"fakeid" TEXT,"alias" TEXT,"nickname" TEXT);'''
                
        '''
            @summary: 微信公众号文章列表
            @param id: 唯一自增ID值
            @param wechat_info_id: 公众号信息的自增id
            @param title: 文章标题
            @param link: 文章链接
            @param digest: 文章描述
        '''
        wechat_list = '''CREATE TABLE "wechat_list"("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"wi_id" INTEGER(11),"title" TEXT,"link" TEXT,"digest" TEXT,"num" INTEGER(11));'''

        '''
            @summary: 用于登录的信息表
            @param id: 唯一自增ID值
            @param uname: 用于登录的用户名
            @param upass: 用于登录的密码
            @param token: 用于登录的token
            @param cookie: 用于登录的cookie
            @param type: 登录类型
        '''
        user_info =  '''CREATE TABLE "user_info"("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"uname" TEXT,"upass" TEXT,"token" TEXT,"cookie" TEXT,"flag" INTEGER(2));'''

        self.create_tables(wechat_info)
        self.create_tables(wechat_list)
        self.create_tables(user_info)
    
    def __close__(self,cursor,conn):
        if cursor: 
            cursor.close()
        if conn:
            conn.close()


