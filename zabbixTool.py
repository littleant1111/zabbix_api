# -*- coding: utf-8 -*-
# !/usr/bin/python
import json
import urllib2
import os

class zabbixTool(object):

    def __init__(self, api_url, user_name, pass_word, uid):
        self._api_url = api_url
        self._user_name = user_name
        self._pass_word = pass_word
        self._uid = uid
        self._auid = self.getAuthId()

    @property
    def api_url(self):
        return self._api_url

    @property
    def user_name(self):
        return self._user_name

    @property
    def pass_word(self):
        return self._pass_word

    @property
    def uid(self):
        return self._uid

    def postData(self, jdata):
        """
        post方法
        """
        req = urllib2.Request(self._api_url, jdata, {"Content-Type": "application/json"})
        response = urllib2.urlopen(req)
        content = json.load(response)
        return content['result']

    def getAuthId(self):
        '''
        获取认证Auth
        :return:
        '''
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'user.login'
        dict_data['params'] = {'user':self._user_name, 'password':self._pass_word}
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        return content

    def getHostGroupList(self):
        '''
        获取主机组列表
        :return:
        '''
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'hostgroup.get'
        dict_data['params'] = {'output':['groupid' ,'name']}
        dict_data['auth'] = self._auid
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        return content

    def getHostList(self,groupid):
        '''
        获取主机列表
        '''
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'host.get'
        dict_data['params'] = {'output':['hostid' ,'name'],'groupids':groupid}
        dict_data['auth'] = self._auid
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        # print '主机列表：gethostone:', content
        return content

    def getItemList(self,hostid):
        '''
        获取某个主机中某项监控对于id号
        '''
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'item.get'
        dict_data['params'] = {'output':['itemids' ,'key_'],'hostids':hostid}
        dict_data['auth'] = self._auid
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        # print 'getitem:', content
        return content

    def getItemHistory(self,itemid,data_type=3):
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'history.get'
        dict_data['params'] = {'output':'extend', 'history':data_type, 'itemids':itemid, 'sortfield':'clock',
                               'sortorder':'DESC', 'limit':1}
        dict_data['auth'] = self._auid
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        # print 'getItemHistory:', content
        return content

    def getGraph(self,itemid):
        dict_data = {}
        dict_data['jsonrpc'] = '2.0'
        dict_data['method'] = 'graph.get'
        dict_data['params'] = {'output': 'extend','itemids':itemid,"sortfield": "name"}
        dict_data['auth'] = self._auid
        dict_data['id'] = self._uid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        # print 'getGraph:', content
        return content

    def logOut(self):
        """
        退出
        :param uid:
        :param authid:
        :return:
        """
        dict_data = {}
        dict_data['method'] = 'user.logOut'
        dict_data['id'] = self._uid
        dict_data['jsonrpc'] = '2.0'
        dict_data['params'] = []
        dict_data['auth'] = self._auid
        jdata = json.dumps(dict_data)
        content = self.postData(jdata)
        return content
    
    def getAllItem(self):
        '''
        获取数据总控制函数
        :return:
        '''
        # 获取主机组列表
        hostgrouplist = self.getHostGroupList()
        # 获取主机组id列表
        hostgroupidlist = []
        for hostgroup in hostgrouplist:
            hostgroupidlist.append(hostgroup['groupid'])
        # 获取主机列表
        hostlist = []
        for hostgroupid in hostgroupidlist:
            hostlist.extend(self.getHostList(hostgroupid))
            # print type(hostlist)
        # 主机id和主机名字典化
        hostdict = {}
        for host in hostlist:
            # print host['hostid']         # 主机id号
            hostdict[host['hostid']] = host['name']
        # 获取监控指标对于id号
        itemdictlist = []
        for id in hostdict:
            itemlist = self.getItemList(id)
            for item in itemlist:
                itemdict = {}
                itemdict['hostid'] = id
                itemdict['hostname'] = hostdict[id]
                itemdict['itemid'] = item['itemid']
                itemdict['itemname'] = item['key_']
                itemdictlist.append(itemdict)
        # print '监控指标对于id号', itemdictlist
        return itemdictlist
