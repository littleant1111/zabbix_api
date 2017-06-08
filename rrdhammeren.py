#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rrdtool


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
    '''
    网卡使用率模板
    '''
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerNetwork, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                               picture_name, picture_show_time, picture_resolution,
                                               picture_title, picture_width, picture_height)

        # RRDHAMMER.__init__(self, rrd_name)

    def create(self):
        '''
        创建网卡rrd数据库
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step,'--start', self.rrd_start_time,
                             # 定义数据源eth1_in(入流量)、eth1_out(出流量)；类型都为GAUGE(不变)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:eth0_in:GAUGE:120:0:U',
                             'DS:eth0_out:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与LAST方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             # 'RRA:LAST:0.5:1:180',
                             # 'RRA:LAST:0.5:5:576',
                             # 'RRA:LAST:0.5:15:672',)
                             'RRA:LAST:0.5:1:3600',
                             'RRA:LAST:0.5:1:10800',
                             'RRA:LAST:0.5:1:86400',)
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
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "DEF:inoctets=%s:eth0_in:LAST" % self.rrd_name,           # 指定网卡入流量数据源DS及CF
                      "DEF:outoctets=%s:eth0_out:LAST" % self.rrd_name,         # 指定网卡出流量数据源DS及CF
                      "CDEF:total=inoctets,outoctets,+",                        # 通过CDEF合并网卡出入流量，得出总流量total
                      "LINE1:total#FF8833:Total traffic",                       # 以线条方式绘制总流量
                      "AREA:inoctets#00FF00:In traffic",                        # 以面积方式绘制入流量
                      "LINE1:outoctets#0000FF:Out traffic",                     # 以线条方式绘制出流量
                      "HRULE:10485760#FF0000:Alarm value\\r",                       # 绘制水平线，作为告警线，阈值为6.1k
                      "CDEF:inbytes=inoctets",
                      "CDEF:outbytes=outoctets",
                      "COMMENT:\\r",                                            # 在网格下方输出一个换行符
                      "GPRINT:inbytes:LAST:LAST IN\: %8.2lf %Sb/s",          # 绘制流入流量平均值
                      "COMMENT:    ",
                      "GPRINT:inbytes:AVERAGE:AVERAGE IN\: %8.2lf %Sb/s",         # 平均值
                      "COMMENT:    ",
                      "GPRINT:inbytes:MAX:MAX IN\: %8.2lf %Sb/s",             # 最大值
                      "COMMENT:    ",
                      "GPRINT:inbytes:MIN:MIN IN\: %8.2lf %Sb/s\\r",          # 最小值
                      "COMMENT:    ",
                      "GPRINT:outbytes:LAST:LAST OUT\: %8.2lf %Sb/s",         # 绘制流出流量平均值
                      "COMMENT:   ",
                      "GPRINT:outbytes:AVERAGE:AVERAGE OUT\: %8.2lf %Sb/s",
                      "COMMENT:   ",
                      "GPRINT:outbytes:MAX:MAX OUT\: %8.2lf %Sb/s",
                      "COMMENT:   ",
                      "GPRINT:outbytes:MIN:MIN OUT\: %8.2lf %Sb/s\\r")


class RrdHammerCPUutilization(RRDHAMMER):
    '''
    CPU使用模板
    '''
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
                             'RRA:LAST:0.5:1:3600',
                             'RRA:LAST:0.5:1:10800',
                             'RRA:LAST:0.5:1:86400',)
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
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--upper-limit", "101", "--lower-limit", "0", "--vertical-label=CPU UsageRate %",
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
                      "COMMENT:Last         Average            Max            Min         \\r",
                      "LINE1:idelss#FF0000:CPU idel time         ",                      # 以线条方式绘制图形idelss
                      "GPRINT:idelss:LAST:%6.2lf %%",                             # 绘制最新值
                      "COMMENT:    ",
                      "GPRINT:idelss:AVERAGE:%5.2lf %%",                          # 绘制平均值
                      "COMMENT:    ",
                      "GPRINT:idelss:MAX:%5.2lf %%",                              # 绘制最大值
                      "COMMENT:    ",
                      "GPRINT:idelss:MIN:%5.2lf %%      \\r",                          # 绘制最小值
                      "LINE1:interruptss#00FF00:CPU interrupt time     ",            # 以线条方式绘制图形interruptss
                      "GPRINT:interruptss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:interruptss:MIN:%5.2lf %%      \\r",
                      "LINE1:iowaitss#0000FF:CPU iowait time        ",                  # 以线条方式绘制图形iowaitss
                      "GPRINT:iowaitss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:iowaitss:MIN:%5.2lf %%      \\r",
                      "LINE1:nicess#FFFF00:CPU nice timei         ",                      # 以线条方式绘制图形nicess
                      "GPRINT:nicess:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:nicess:MIN:%5.2lf %%      \\r",
                      "LINE1:softirgss#A67D3D:CPU softirg time       ",                # 以线条方式绘制图形softirgss
                      "GPRINT:softirgss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:softirgss:MIN:%5.2lf %%      \\r",
                      "LINE1:stealss#FF7F00:CPU steal time         ",                    # 以线条方式绘制图形stealss
                      "GPRINT:stealss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:stealss:MIN:%5.2lf %%      \\r",
                      "LINE1:systemss#D8D8BF:CPU system time        ",                  # 以线条方式绘制图形systemss
                      "GPRINT:systemss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:systemss:MIN:%5.2lf %%      \\r",
                      "LINE1:userss#CD7F32:CPU user time          ",                      # 以线条方式绘制图形userss
                      "GPRINT:userss:LAST:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:AVERAGE:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:MAX:%5.2lf %%",
                      "COMMENT:    ",
                      "GPRINT:userss:MIN:%5.2lf %%      \\r",)


class RrdHammerCPUload(RRDHAMMER):
    '''
    CPU load 使用率模板
    '''
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerCPUload, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                               picture_name, picture_show_time, picture_resolution,
                                               picture_title, picture_width, picture_height)

        # RRDHAMMER.__init__(self, rrd_name)

    def create(self):
        '''
        创建cpu load rrd数据库
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step,'--start', self.rrd_start_time,
                             # 定义数据源cpu_load 1 min(1分钟使用率) cpu_load 1 min(1分钟使用率) cpu_load 5 min(5分钟使用率)；
                             # cpu_load 15 min(15分钟使用率) 类型都为GAUGE(不变)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:cpuloadone:GAUGE:120:0:U',
                             'DS:cpuloadfive:GAUGE:120:0:U',
                             'DS:cpuloadfifteen:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与LAST方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             'RRA:LAST:0.5:1:3600',
                             'RRA:LAST:0.5:1:10800',
                             'RRA:LAST:0.5:1:86400',)
        if rrd:
            return rrdtool.error()

    def update(self, rrd_update_time, cpuloadone, cpuloadfive, cpuloadfifteen):
        '''
        接收数据更新cpu load rrd数据库
        '''
        update = rrdtool.updatev(self.rrd_name,
                                 '%s:%s:%s:%s' % (str(rrd_update_time), str(cpuloadone), str(cpuloadfive),
                                                  str(cpuloadfifteen)))
        if update:
            return rrdtool.error()

    def graph(self):
        '''
        根据cpu load 数据库绘图
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time,
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--vertical-label=CPU Load", "--upper-limit", "3.0001", "--lower-limit", "0.0001",
                      "DEF:cpuloadone=%s:cpuloadone:LAST" % self.rrd_name,          # 指定1分钟负载数据源DS及CF
                      "DEF:cpuloadfive=%s:cpuloadfive:LAST" % self.rrd_name,        # 指定5分钟数据源DS及CF
                      "DEF:cpuloadfifteen=%s:cpuloadfifteen:LAST" % self.rrd_name,  # 指定15分钟数据源DS及CF
                      # "HRULE:10485760#FF0000:Alarm value\\r",                     # 绘制水平线，作为告警线，阈值为xx
                      "CDEF:cpuloadoness=cpuloadone",
                      "CDEF:cpuloadfives=cpuloadfive",
                      "CDEF:cpuloadfifteens=cpuloadfifteen",
                      "COMMENT:\\r",                                                         # 在网格下方输出一个换行符
                      "COMMENT:Last           Min             Average           Max                \\r",
                      "LINE1:cpuloadone#00FF00:Processor load (1 min average per core)    ",     # 以线条方式绘制1分钟负载
                      "GPRINT:cpuloadoness:LAST:%5.4lf ",                                   # 最新值
                      "COMMENT:    ",
                      "GPRINT:cpuloadoness:MIN:%5.4lf ",                                    # 最小值
                      "COMMENT:    ",
                      "GPRINT:cpuloadoness:AVERAGE:%5.4lf    ",                              # 平均值
                      "COMMENT:    ",
                      "GPRINT:cpuloadoness:MAX:%5.4lf              \\r",                # 最大值
                      "LINE1:cpuloadfive#0000FF:Processor load (5 min average per core)    ",    # 以线条方式绘制5分钟负载
                      "GPRINT:cpuloadfives:LAST:%5.4lf ",                                   # 同上
                      "COMMENT:    ",
                      "GPRINT:cpuloadfives:MIN:%5.4lf ",
                      "COMMENT:    ",
                      "GPRINT:cpuloadfives:AVERAGE:%5.4lf    ",
                      "COMMENT:    ",
                      "GPRINT:cpuloadfives:MAX:%5.4lf              \\r",
                      "LINE1:cpuloadfifteen#FF00FF:Processor load (15 min average per core)   ",  # 以线条方式绘制15分钟负载
                      "GPRINT:cpuloadfifteens:LAST:%5.4lf ",
                      "COMMENT:    ",
                      "GPRINT:cpuloadfifteens:MIN:%5.4lf ",
                      "COMMENT:    ",
                      "GPRINT:cpuloadfifteens:AVERAGE:%5.4lf    ",
                      "COMMENT:    ",
                      "GPRINT:cpuloadfifteens:MAX:%5.4lf              \\r",)


class RrdHammerMemoryUse(RRDHAMMER):
    '''
    内存使用率模板
    '''
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerMemoryUse, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                                 picture_name, picture_show_time, picture_resolution,
                                                 picture_title, picture_width, picture_height)

        # RRDHAMMER.__init__(self, rrd_name)

    def create(self):
        '''
        创建memory user rrd数据库
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step, '--start', self.rrd_start_time,
                             # 定义数据源Available memory(可用内存)、Total memory(总内存)；类型都为GAUGE(不变)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:total:GAUGE:120:0:U',
                             'DS:availabel:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与LAST方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             'RRA:LAST:0.5:1:3600',
                             'RRA:LAST:0.5:1:10800',
                             'RRA:LAST:0.5:1:86400',)
        if rrd:
            return rrdtool.error()

    def update(self, rrd_update_time, total_memory, available_memory):
        '''
        接收数据更新memory user rrd数据库
        '''
        update = rrdtool.updatev(self.rrd_name,
                                 '%s:%s:%s' % (str(rrd_update_time), str(available_memory), str(total_memory)))
        if update:
            return rrdtool.error()

    def graph(self,):
        '''
        根据 memory user 数据库绘图
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time,
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--vertical-label= MemoryUse ", "--lower-limit", "0.1",
                      "DEF:total_memory=%s:total:LAST" % self.rrd_name,             # 指定总内存数据源DS及CF
                      "DEF:availabel_memory=%s:availabel:LAST" % self.rrd_name,     # 指定可用内存数据源DS及CF
                      # "HRULE:4018638848#008000:Alarm value",                      # 绘制水平线，作为告警线，阈值为xx
                      "CDEF:total_memorys=total_memory,1073741824,/",
                      "CDEF:availabel_memorys=availabel_memory,1073741824,/",
                      "COMMENT:\\r",                                                 # 在网格下方输出一个换行符
                      "AREA:total_memory#90EE90:Total memory \:",                    # 总内存线
                      "GPRINT:total_memorys:AVERAGE: %4.2lf GB \\r",                    # 最新值
                      "COMMENT:              Last           Min           Average          Max                       \
                      \\r",
                      "AREA:availabel_memory#00FFFF:Availabel memory",
                      "GPRINT:availabel_memorys:LAST: %4.2lf GB",                   # 最新值
                      "COMMENT:   ",
                      "GPRINT:availabel_memorys:MIN: %4.2lf GB",                    # 最小值
                      "COMMENT:   ",
                      "GPRINT:availabel_memorys:AVERAGE: %3.2lf GB",                # 平均值
                      "COMMENT:   ",
                      "GPRINT:availabel_memorys:MAX: %5.2lf GB                                         \\r",
                      "COMMENT:\\r",)  # 在网格下方输出一个换行符


class RrdHammerHardDisk(RRDHAMMER):
    '''
    内存使用率模板
    '''
    def __init__(self, rrd_name, rrd_step, rrd_start_time,
                 picture_name, picture_show_time, picture_resolution,
                 picture_title, picture_width, picture_height):
        super(RrdHammerHardDisk, self).__init__(rrd_name, rrd_step, rrd_start_time,
                                                picture_name, picture_show_time, picture_resolution,
                                                picture_title, picture_width, picture_height)

        # RRDHAMMER.__init__(self, rrd_name)

    def create(self):
        '''
        创建hard disk rrd数据库
        '''
        rrd = rrdtool.create(self.rrd_name, '--step', self.rrd_step, '--start', self.rrd_start_time,
                             # 定义数据源base hard(/)、boot(/boot)；/home(家目录)；120秒为心跳值，
                             # 其含义是120秒没有收到值，则会用UNKNOWN代替；0为最小值；最大值用U代替，表示不确定
                             'DS:hardfree:GAUGE:120:0:U',
                             'DS:hardtotal:GAUGE:120:0:U',
                             # xff定义为0.5，表示一个CDP中的PDP值如超过一半值为UNKNOWN，则该CDP的值就被标为UNKNOWN
                             # 下列前3个RRA的定义说明如下，其他定义与LAST方式相似，区别是存最大值与最小值
                             # 每隔1分钟(1*60秒)存一次数据的平均值,存60笔
                             'RRA:LAST:0.5:1:3600',
                             'RRA:LAST:0.5:1:10800',
                             'RRA:LAST:0.5:1:86400',)
        if rrd:
            return rrdtool.error()

    def update(self, rrd_update_time, hardfree, hardtotal):
        '''
        接收数据更新hard disk rrd数据库
        '''
        update = rrdtool.updatev(self.rrd_name,
                                 '%s:%s:%s' % (str(rrd_update_time), str(hardfree), str(hardtotal)))
        if update:
            return rrdtool.error()

    def graph(self,):
        '''
        根据 hard disk 数据库绘图   单位为  G
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time,
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--vertical-label= HardUse ",
                      "DEF:total_hard=%s:hardtotal:LAST" % self.rrd_name,             # 指定总硬盘数据源DS及CF
                      "DEF:free_hard=%s:hardfree:LAST" % self.rrd_name,               # 指定可用硬盘数据源DS及CF
                      # "HRULE:4018638848#008000:Alarm value",                        # 绘制水平线，作为告警线，阈值为xx
                      "CDEF:total_hards=total_hard,1073741824,/",                     # 换算成 G
                      "CDEF:free_hards=free_hard,1073741824,/",
                      "COMMENT:\\r",                                                  # 在网格下方输出一个换行符
                      "LINE2:total_hard#FF0000:Total \:",
                      "GPRINT:total_hards:LAST: %4.2lf G \\r",                        # 最新值
                      "AREA:free_hard#3CB371: Free \:",
                      "GPRINT:free_hards:LAST: %4.2lf G \\r",
                      "COMMENT:\\r",)  # 在网格下方输出一个换行符

    def graphboot(self,):
        '''
        根据 hard disk 数据库绘图  单位为 M
        '''
        rrdtool.graph(self.picture_name, "--start", self.picture_show_time,
                      # "--x-grid", "MINUTE:5:MINUTE:15:MINUTE:15:0:%H:%M",
                      "--x-grid", "MINUTE:20:HOUR:1:HOUR:2:0:%H:%M",
                      "--width", self.picture_width, "--height", self.picture_height, "--title", self.picture_title,
                      "--vertical-label= HardUse ",
                      "DEF:total_hard=%s:hardtotal:LAST" % self.rrd_name,             # 指定总硬盘数据源DS及CF
                      "DEF:free_hard=%s:hardfree:LAST" % self.rrd_name,               # 指定可用硬盘数据源DS及CF
                      # "HRULE:4018638848#008000:Alarm value",                        # 绘制水平线，作为告警线，阈值为xx
                      "CDEF:total_hards=total_hard,1048576,/",                        # 换算成 M
                      "CDEF:free_hards=free_hard,1048576,/",
                      "COMMENT:\\r",                                                  # 在网格下方输出一个换行符
                      "LINE2:total_hard#FF0000:Total \:",
                      "GPRINT:total_hards:LAST: %4.2lf M \\r",                        # 最新值
                      "AREA:free_hard#3CB371: Free \:",
                      "GPRINT:free_hards:LAST: %4.2lf M \\r",
                      "COMMENT:\\r",)  # 在网格下方输出一个换行符

# 内存测试样例
# t = RrdHammerMemoryUse("a.rrd", "1", "1480587064", "a.png", "-1H", "1", "TTTTTTTTT", "800", "300")
# t.create()
# t.update("1480587164", "1996021760", "4018638848",)
# t.update("1480587264", "1996321760", "4018638848",)
# t.update("1480587364", "1996221760", "4018638848",)
# t.update("1480587464", "1993021760", "4018638848",)
# t.graph()
# print "------0k------"
