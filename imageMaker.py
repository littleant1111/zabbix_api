# -*- coding:utf-8 -*-
#!/bin/env python

from rrdhammeren import *
import sys
import logging
import logw
import json
import time
import os
import MySQLdb


class imageMaker(object):
    def __init__(self, zb, **dic):
        self.ip = dic['ip']
        self.monitortype = dic['monitortype']
        self.monitorsub = dic['monitorsub']
        self.timespan = dic['timespan']
        self.width = str(dic['width'])
        self.height = str(dic['height'])
        # 设置rrd数据库名
        self.rrdname = self.ip + '_' + self.monitortype + '_' + self.monitorsub+self.timespan
        pwd = os.getcwd()

        logname = sys.argv[0].split("/")[len(sys.argv[0].split("/")) - 1][0:-3]
        logdir = '{p}/log/'.format(p=pwd)
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        logw.log_w(20, logdir + self.ip + self.monitortype + self.monitorsub + logname + '.log')
        # 设置图片存储路径
        rrdbdir = '{p}/rrddb'.format(p=pwd)
        if not os.path.exists(rrdbdir):
            os.mkdir(rrdbdir)
        # 设置 图片、rrd数据库路径
        self.pname = '/home/bqadm/django/button/app/static/img/zabbix_pic/{n}.png'.format( n=self.rrdname)
        self.rname = '{p}/{n}.rrd'.format(p=rrdbdir, n=self.rrdname)
        # 获取当前时间
        localtime = str(int(time.time()) - 300)
        # 设置图片标题
        title = self.rrdname + "(" + time.strftime('%Y-%m-%d', time.localtime(
                                 time.time())) + ")"
        titlestr = title.encode('utf-8')
        # 判断监控类型并初始化数据
        if 'net' in self.monitortype: 
            self.rrdhammer = RrdHammerNetwork(self.rname, '1', localtime, self.pname, self.timespan, '1', titlestr,
                                              self.width, self.height)
        if 'cpu.util' in self.monitortype:
            self.rrdhammer = RrdHammerCPUutilization(self.rname, '1', localtime, self.pname, self.timespan, '1',
                                                     titlestr, self.width, self.height)
        if 'cpu.load' in self.monitortype:
            self.rrdhammer = RrdHammerCPUload(self.rname, '1', localtime, self.pname, self.timespan, '1',
                                              titlestr, self.width, self.height)

        if 'vm.memory.size' in self.monitortype:
            self.rrdhammer = RrdHammerMemoryUse(self.rname, '1', localtime, self.pname, self.timespan, '1', titlestr,
                                                self.width, self.height)
        # 创建rrd数据库
        if not os.path.exists(self.rname): 
            self.rrdhammer.create()

        sql = """insert into rrd_image_info(ip,type,sub,timespan,image_path,db_path) select %s,%s,%s,%s,
           %s,%s from dual where not exists( select ip,type,sub FROM
           rrd_image_info where ip=%s and type=%s and sub=%s and timespan=%s)"""
        param = (self.ip, self.monitortype, self.monitorsub, self.timespan, self.pname, self.rname, self.ip,
                 self.monitortype, self.monitorsub, self.timespan)
        self.writeDb(sql, param)
        self.zabbixtool = zb
        self.allitemdictlist = zb.getAllItem()


    def getMonitorItemData(self):
        param_list = []
        sql = """insert into zabbix_trans_log(clock,clocktime,hostid,hostname,itemid,itemname,value) select %s,%s,%s,%s,%s,%s,%s
                 from dual where not exists(select 1 from zabbix_trans_log where clocktime=%s and itemid=%s)"""
        for item in self.allitemdictlist:
            if 'net' in self.monitortype:
                if self.monitortype in item['itemname'] and self.ip in item['hostname']:
                      
                    clock = self.zabbixtool.getItemHistory(item['itemid'], data_type=3)[0]['clock']
                    clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                    hostid = item['hostid']
                    hostname = item['hostname']
                    itemid = item['itemid']
                    itemname = item['itemname']
                    value = self.zabbixtool.getItemHistory(item['itemid'], data_type=3)[0]['value']
                    param = (clock, clocktime, hostid, hostname, itemid, itemname, value,clocktime,itemid)
                    param_list.append(param)
                    self.writeDb(sql, param)
                    
            if 'cpu.util' in self.monitortype:
                if self.monitortype in item['itemname'] and  self.ip in item['hostname']:
                    clock = self.zabbixtool.getItemHistory(item['itemid'], data_type=0)[0]['clock']
                    clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                    hostid = item['hostid']
                    hostname = item['hostname']
                    itemid = item['itemid']
                    itemname = item['itemname']
                    value = self.zabbixtool.getItemHistory(item['itemid'], data_type=0)[0]['value']
                    param = (clock, clocktime, hostid, hostname, itemid, itemname, value,clocktime,itemid)
                    param_list.append(param)
                    self.writeDb(sql, param)

            if 'cpu.load' in self.monitortype:
                if self.monitortype in item['itemname'] and self.ip in item['hostname']:
                    clock = self.zabbixtool.getItemHistory(item['itemid'], data_type=0)[0]['clock']
                    clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                    hostid = item['hostid']
                    hostname = item['hostname']
                    itemid = item['itemid']
                    itemname = item['itemname']
                    value = self.zabbixtool.getItemHistory(item['itemid'], data_type=0)[0]['value']
                    param = (clock, clocktime, hostid, hostname, itemid, itemname, value,clocktime,itemid)
                    param_list.append(param)
                    self.writeDb(sql, param)
                    
            if 'vm.memory.size' in self.monitortype:
                if self.monitortype in item['itemname'] and  self.ip in item['hostname']:
                    if 'available' in item['itemname'] or 'total' in item['itemname']:
                        zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=3)[0]
                        clock = zb_gethistory['clock']
                        clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                        hostid = item['hostid']
                        hostname = item['hostname']
                        itemid = item['itemid']
                        itemname = item['itemname']
                        value = zb_gethistory['value']
                        param = (clock,clocktime,hostid,hostname, itemid, itemname, value,clocktime,itemid)
                        param_list.append(param)
                        self.writeDb(sql, param)

            if 'vfs.fs.size' in self.monitortype:
                if self.monitortype in item['itemname'] and  self.ip in item['hostname'] and 'pfree' not in item['itemname'] and ',used' not in item['itemname']:
                    zb_gethistory = self.zabbixtool.getItemHistory(item['itemid'], data_type=3)[0]
                    clock = zb_gethistory['clock']
                    clocktime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(clock)))
                    hostid = item['hostid']
                    hostname = item['hostname']
                    itemid = item['itemid']
                    itemname = item['itemname']
                    value = zb_gethistory['value']
                    param = (clock,clocktime,hostid,hostname, itemid, itemname, value,clocktime,itemid)
                    param_list.append(param)
                    self.writeDb(sql, param)
        return param_list

    def updateImage(self):
        param_list = self.getMonitorItemData()
        state_time = 0
        traffic_in_value = 0
        traffic_out_value = 0
        if 'net' in self.monitortype: 
            for param in param_list:
                if 'net.if.in' in param[5]:
                    traffic_in_value = param[6]
                if 'net.if.out' in param[5]:
                    traffic_out_value = param[6]
                state_time = param[0]
            logging.info('{0}  {1}  {2}  {3}'.format(self.rrdname, state_time, traffic_in_value, traffic_out_value))
            self.rrdhammer.update(state_time, traffic_in_value,
                                  traffic_out_value)
             
            self.rrdhammer.graph()
          
        if 'cpu.util' in self.monitortype:
            for param in param_list:
                if ',interrupt' in param[5]:
                    cpu_interrupt = param[6]
                if ',iowait' in param[5]:
                    cpu_iowait = param[6] 
                if ',idle' in param[5]:
                    cpu_idle = param[6]
                if ',nice' in param[5]:
                    cpu_nice = param[6]
                if ',softirq' in param[5]:
                    cpu_softirq = param[6]
                if ',steal' in param[5]:
                    cpu_steal = param[6] 
                if ',system' in param[5]:
                    cpu_system = param[6]
                if ',user' in param[5]: 
                    cpu_user = param[6]
                state_time = param[0]
            logging.info('{0}  {1}  {2}  {3} {4} {5} {6} {7} {8} {9}'.format(self.rrdname, state_time,cpu_idle,
                   cpu_interrupt, cpu_iowait, cpu_nice,
                   cpu_softirq, cpu_steal, cpu_system, cpu_user))
            self.rrdhammer.update( state_time, cpu_idle,
                   cpu_interrupt, cpu_iowait, cpu_nice,
                   cpu_softirq, cpu_steal, cpu_system, cpu_user)
             
            self.rrdhammer.graph()

        if 'cpu.load' in self.monitortype:
            for param in param_list:
                if 'all,avg1' in param[5]:
                    cpu_avg1 = param[6]
                if 'all,avg5' in param[5]:
                    cpu_avg5 = param[6]
                if 'all,avg15' in param[5]:
                    cpu_avg15 = param[6]
                state_time = param[0]
            logging.info('{0}  {1}  {2}  {3} {4} '.format(self.rrdname, state_time, cpu_avg1, cpu_avg5, cpu_avg15))
            self.rrdhammer.update(state_time, cpu_avg1, cpu_avg5, cpu_avg15)

            self.rrdhammer.graph()

        if 'memory' in self.monitortype:
            for param in param_list:
                if 'available' in param[5]:
                    available = param[6]
                    state_time = param[0]
                if 'total' in param[5]:
                    total = param[6]
            logging.info('{0}  {1}  {2} {3}'.format(self.rrdname, state_time,available,total))
            self.rrdhammer.update(state_time,available,total)

            self.rrdhammer.graph() 


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
        except Execption as e:
            print e
            conn.rollback()
        cur.close()
        conn.close()

