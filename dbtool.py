# -*- coding:utf-8 -*-
#!/bin/env python


import json
import time
import os
import MySQLdb


class imageMaker(object):
    def __init__(self, zb, **dic):
        self.ip = dic['ip']

        self.zabbixtool = zb
        self.allitemdictlist = zb.getAllItem()


    def etMonitorItemData(self):
        sql = """insert into zabbix_trans_log(clock,clocktime,hostid,hostname,itemid,itemname,value) select %s,%s,%s,%s,%s,%s,%s
                 from dual where not exists(select 1 from zabbix_trans_log where clocktime=%s and itemid=%s)"""
        pid = os.getpid()

        for item in self.allitemdictlist:
            if self.ip in item['hostname']:
                zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=3)
                if len(zb_gethistory) == 0:
                    zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=1)
                if len(zb_gethistory) == 0:
                    zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=2)
                if len(zb_gethistory) == 0:
                    zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=4)
                if len(zb_gethistory) == 0:
                    zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=0)
                if len(zb_gethistory) == 0:
                    continue
                zb_gethistory=zb_gethistory[0]
                clock = zb_gethistory['clock']
                clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                hostid = item['hostid']
                hostname = item['hostname']
                itemid = item['itemid']
                itemname = item['itemname']
                value = zb_gethistory['value']
                param = (clock, clocktime, hostid, hostname, itemid, itemname, value, clocktime, itemid)
                self.writeDb(sql, param)


    def writeDb(self,sql,param):
        '''
        写数据库信息
        '''
        sqlconfigfile = open('.' + os.sep + 'config' + os.sep + 'mysql_config.json')
        sqlconfigdict = json.load(sqlconfigfile)
        conn = MySQLdb.connect(host=sqlconfigdict['ip'], port=sqlconfigdict['port'],
                               user=sqlconfigdict['username'], passwd=sqlconfigdict['password'],
                               db=sqlconfigdict['database'], charset=sqlconfigdict['charset'])
        cur = conn.cursor()
        try:
            cur.execute(sql, param)
            conn.commit()
        except Exception , e:
            print e
            conn.rollback()
        cur.close()
        conn.close()

