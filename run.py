# -*- coding:utf-8 -*-
#!/bin/env python

from zabbixTool import *
from dbtool import imageMaker
import json
import os
import time
from multiprocessing import Pool

from multiprocessing import cpu_count

def multirun(args):

    api_url = 'http://10.40.1.26/zabbix/api_jsonrpc.php'
    user_name = 'fengchao'
    pass_word = '1qwe@76ER'
    uid = args[0]
    zb = zabbixTool(api_url=api_url, user_name=user_name, pass_word=pass_word, uid=uid)          # 初始化参数
    print "当前进程参数列表 %s " % args
    immk = imageMaker(zb, ip=args[1])
    while True:
        try:
            immk.getMonitorItemData()
            # zb.logOut()
            # zb = zabbixTool(api_url=api_url, user_name=user_name, pass_word=pass_word, uid=uid)  # 初始化参数
            # immk = imageMaker(zb, ip=args[1])
        except Exception , e:
            print 'Exception()',e
            zb.logOut()
        time.sleep(61)


if __name__ == '__main__':
    args = []
    jfile = open('.'+os.sep+'config'+os.sep+'monitor.json')
    jdict = json.load(jfile)                                                       # 获取配置文件信息
    print jdict
    for key in jdict:

        jdict[key].insert(0, key)
        args.append(jdict[key])                                                    # 以列表的方式获取配置参数
    print "获取配置文件列表 \n %s" % args
    try:
        monitorpool = Pool(len(args)+1)                                          # 以多进程的方式启动调用上方multirun函数
        monitorpool.map_async(multirun, args)
        monitorpool.close()
        monitorpool.join()
    except Exception as e:
        print e



