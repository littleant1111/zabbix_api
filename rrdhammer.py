#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rrdtool
import os


class RRDHAMMER(object):
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        self.rrd_name = str(rrd_name)                         # rrd数据库名
        self.rrd_step = str(rrd_step)                         # rrd数据库解析度
        self.rrd_start_time = str(rrd_start_time)             # rrd数据库开始计数时间
        self.picture_name = str(picture_name)                 # 图片名称
        self.picture_show_time = str(picture_show_time)       # 图片显示时长 如"-1H"
        self.picture_resolution = str(picture_resolution)     # 图片解析度
        self.picture_title = str(picture_title)               # 图片上方显示标题\
        # 如 "Server network traffic 3H flow (" + time.strftime('%Y-%m-%d', time.localtime(time.time())) + ")"
        self.picture_width = str(picture_width)               # 图片宽度 单位像素
        self.picture_height = str(picture_height)             # 图片高度 单位像素


class RrdHammerNetwork(RRDHAMMER):
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerNetwork, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                               picture_name, picture_show_time, picture_resolution,
                                               picture_title, picture_width, picture_height)

        # RRDHAMMER.__init__(self, rrd_name)

    def create(self):
        '''
        创建网卡rrd数据库，默认路径为当前路径下rrddb文件夹下
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step,'--start', self.rrd_start_time,
                             # 定义数据源eth1_in(入流量)、eth1_out(出流量)；类型都为GAUGE(不变)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:eth0_in:GAUGE:120:0:U',
                             'DS:eth0_out:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与LAST方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             # 每隔5分钟(5*60秒)存一次数据的平均值,存12笔
                             # 每隔15分钟(15*60秒)存一次数据的平均值,存4笔
                             'RRA:LAST:0.5:1:180',
                             'RRA:LAST:0.5:5:576',
                             'RRA:LAST:0.5:15:672',)
        if rrd:
            return rrdtool.error()

    def update(self, rrd_update_time, input_traffic, output_traffic):
        '''
        接收数据更新网卡rrd数据库
        '''
        update = rrdtool.updatev(self.rrd_name,
                                 '%s:%s:%s' % (str(rrd_update_time), str(input_traffic), str(output_traffic)))
        if update:
            return rrdtool.error()

    def graph(self):
        '''
        根据网卡数据库绘图
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time, "--vertical-label=Bytes/s",
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "DEF:inoctets=%s:eth0_in:LAST" % self.rrd_name,           # 指定网卡入流量数据源DS及CF
                      "DEF:outoctets=%s:eth0_out:LAST" % self.rrd_name,         # 指定网卡出流量数据源DS及CF
                      "CDEF:total=inoctets,outoctets,+",                        # 通过CDEF合并网卡出入流量，得出总流量total
                      "LINE1:total#FF8833:Total traffic",                       # 以线条方式绘制总流量
                      "AREA:inoctets#00FF00:In traffic",                        # 以面积方式绘制入流量
                      "LINE1:outoctets#0000FF:Out traffic",                     # 以线条方式绘制出流量
                      "HRULE:6144#FF0000:Alarm value\\r",                       # 绘制水平线，作为告警线，阈值为6.1k
                      "CDEF:inbytes=inoctets",
                      "CDEF:outbytes=outoctets",
                      "COMMENT:\\r",                                            # 在网格下方输出一个换行符
                      "GPRINT:inbytes:LAST:最新流入流量\: %8.2lf %Sb/s",          # 绘制流入流量平均值
                      "COMMENT:    ",
                      "GPRINT:inbytes:AVERAGE:流入平均量\: %8.2lf %Sb/s",         # 平均值
                      "COMMENT:    ",
                      "GPRINT:inbytes:MAX:流入最大量\: %8.2lf %Sb/s",             # 最大值
                      "COMMENT:    ",
                      "GPRINT:inbytes:MIN:流入最小量\: %8.2lf %Sb/s\\r",          # 最小值
                      "COMMENT:    ",
                      "GPRINT:outbytes:LAST:最新流出流量\: %8.2lf %Sb/s",         # 绘制流出流量平均值
                      "COMMENT:    ",
                      "GPRINT:outbytes:AVERAGE:流出平均量\: %8.2lf %Sb/s",
                      "COMMENT:    ",
                      "GPRINT:outbytes:MAX:流出最大量\: %8.2lf %Sb/s",
                      "COMMENT:    ",
                      "GPRINT:outbytes:MIN:流出最小量\: %8.2lf %Sb/s\\r",
                      "COMMENT:                                                                   佰仟金融")


class RrdHammerCPUutilization(RRDHAMMER):
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerCPUutilization, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                                      picture_name, picture_show_time, picture_resolution,
                                                      picture_title, picture_width, picture_height)
         # HAMMER.__init__(self,rrd_name)

    def create(self):
        '''
        创建CPUutilization rrd数据库，默认路径为当前路径下rrddb文件夹下
        :return:
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step, '--start', self.rrd_start_time,
                             # 定义数据源idle、interrupt、iowait、nice、softirg、steal、system、user；类型都为GAUGE(不变)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:idle:GAUGE:120:0:U',
                             'DS:interrupt:GAUGE:120:0:U',
                             'DS:iowait:GAUGE:120:0:U',
                             'DS:nice:GAUGE:120:0:U',
                             'DS:softirg:GAUGE:120:0:U',
                             'DS:steal:GAUGE:120:0:U',
                             'DS:system:GAUGE:120:0:U',
                             'DS:user:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与AVERAGE方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             # 每隔5分钟(5*60秒)存一次数据的平均值,存12笔
                             # 每隔15分钟(15*60秒)存一次数据的平均值,存4笔
                             'RRA:LAST:0.5:1:180',
                             'RRA:LAST:0.5:5:576',
                             'RRA:LAST:0.5:15:672', )
        if rrd:
            return rrdtool.error()

    def update(self, rrd_update_time,cpu_idle,cpu_interrupt, cpu_iowait, cpu_nice,
               cpu_softirg, cpu_steal, cpu_system, cpu_user):
        '''
        接收数据更新CPUutilization rrd数据库
        特定参数,依据DS源而定 cpu_idle、cpu_interrupt、cpu_iowait、cpu_nice、cpu_softirg、cpu_steal、cpu_system、cpu_user
        '''
        update = rrdtool.updatev(self.rrd_name,
                                 '%s:%s:%s:%s:%s:%s:%s:%s:%s' % (str(rrd_update_time), str(cpu_idle), str(cpu_interrupt),
                                                                 str(cpu_iowait), str(cpu_nice), str(cpu_softirg),
                                                                 str(cpu_steal), str(cpu_system), str(cpu_user)))
        if update:
            return rrdtool.error()

    def graph(self):
        '''
        根据CPUutilization rrd数据库绘图
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time, "--step", self.picture_resolution,
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--upper-limit", "100", "--lower-limit", "0","--vertical-label=CPU使用率 %",
                      "DEF:idels=%s:idle:LAST" % self.rrd_name,
                      "DEF:interrupts=%s:interrupt:LAST" % self.rrd_name,
                      "DEF:iowaits=%s:iowait:LAST" % self.rrd_name,
                      "DEF:nices=%s:nice:LAST" % self.rrd_name,
                      "DEF:softirgs=%s:softirg:LAST" % self.rrd_name,
                      "DEF:steals=%s:steal:LAST" % self.rrd_name,
                      "DEF:systems=%s:system:LAST" % self.rrd_name,
                      "DEF:users=%s:user:LAST" % self.rrd_name,
                      "CDEF:idelss=idels",
                      "CDEF:interruptss=interrupts",
                      "CDEF:iowaitss=iowaits",
                      "CDEF:nicess=nices",
                      "CDEF:softirgss=softirgs",
                      "CDEF:stealss=steals",
                      "CDEF:systemss=systems",
                      "CDEF:userss=users",
                      "COMMENT:\\r",                                            # 在网格下方输出一个换行符
                      "COMMENT:\t\t\t\t\t\t   最新值          平均值           最大值           最小值\t\t\\r",
                      "LINE1:idelss#FF0000:CPU idel time\t\t",                      # 以线条方式绘制图形idelss
                      "GPRINT:idelss:LAST:%5.2lf %%",                             # 绘制最新值
                      "COMMENT:    ",
                      "GPRINT:idelss:AVERAGE:%5.2lf %%",                          # 绘制平均值
                      "COMMENT:    ",
                      "GPRINT:idelss:MAX:%5.2lf %%",                              # 绘制最大值
                      "COMMENT:    ",
                      "GPRINT:idelss:MIN:%5.2lf %%\t\t\\r",                          # 绘制最小值
                      "LINE1:interruptss#00FF00:CPU interrupt time\t",            # 以线条方式绘制图形interruptss
                      "GPRINT:interruptss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:iowaitss#0000FF:CPU iowait time    \t",                  # 以线条方式绘制图形iowaitss
                      "GPRINT:iowaitss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:nicess#FFFF00:CPU nice timei    \t",                      # 以线条方式绘制图形nicess
                      "GPRINT:nicess:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:softirgss#A67D3D:CPU softirg time    \t",                # 以线条方式绘制图形softirgss
                      "GPRINT:softirgss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:stealss#FF7F00:CPU steal time    \t",                    # 以线条方式绘制图形stealss
                      "GPRINT:stealss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:systemss#D8D8BF:CPU system time    \t",                  # 以线条方式绘制图形systemss
                      "GPRINT:systemss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:MIN:%5.2lf %%\t\t\\r",
                      "LINE1:userss#CD7F32:CPU user time\t\t",                      # 以线条方式绘制图形userss
                      "GPRINT:userss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:MIN:%5.2lf %%\t\t\\r",)

# 实例化测试样例 注意时间 否则看不到图像

