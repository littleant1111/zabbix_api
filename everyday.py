#!/bin/python
# -*- coding:utf-8 -*-
import os
import datetime
import MySQLdb
import json
def writeDb():
    '''
    写数据库信息
    '''
    sqlconfigfile = open('.' + os.sep + 'config' + os.sep + 'mysql_config.json')
    sqlconfigdict = json.load(sqlconfigfile)
    print sqlconfigdict
    conn = MySQLdb.connect(host=sqlconfigdict['ip'], port=sqlconfigdict['port'],
                           user=sqlconfigdict['username'], passwd=sqlconfigdict['password'],
                           db=sqlconfigdict['database'], charset=sqlconfigdict['charset'])
    cur = conn.cursor()
    try:
    	sql = """delete  from zabbix_trans_log where flowtime< %s"""
        today=str(datetime.date.today())
        cur.execute(sql,[today])
        conn.commit()
    except Execption as e:
        print e
        conn.rollback()
    cur.close()
    conn.close()
writeDb()
