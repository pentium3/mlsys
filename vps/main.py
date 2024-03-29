#! /usr/bin/env python
# -*- coding: utf-8 -*-

# VPS side
import zmq
import sys
import os
import time
from concurrent import futures
import psutil
import json
from concurrent.futures import ThreadPoolExecutor

context=zmq.Context()
socket=context.socket(zmq.REQ)
socket.connect("tcp://192.168.122.1:5555")
#socket.connect("tcp://127.0.0.1:5555")

MonitorList=['CPUUSG', 'MEMUSG', 'IORRAT', 'IOWRAT']

def GetStatMetric():
    ans={}
    for _l in MonitorList:
        ans[_l]=[]
    hd1info=list(psutil.disk_io_counters())
    cpuinfo=str(psutil.cpu_percent(interval=1, percpu=False))
    hd2info=list(psutil.disk_io_counters())
    meminfo=str(psutil.virtual_memory().percent)
    hdread=str(hd2info[2]-hd1info[2])
    hdwrite=str(hd2info[3]-hd1info[3])
    ans['CPUUSG']=cpuinfo
    ans['MEMUSG']=meminfo
    ans['IORRAT']=hdread
    ans['IOWRAT']=hdwrite
    return (ans)

def RunBenchmark(type):
    benchdir=os.path.join(os.getcwd(),'benchmark',type)
    sys.path.append(benchdir)
    print("RunBenchmark " + benchdir)
    import bench as pb
    ans=pb.Bench().Run()
    del pb
    sys.path.remove(benchdir)
    return (ans)

#Run benchmark and monitor CPU/MEM/IO at the same time
def RunBenchmarkPool(request):
    print("RunBenchmarkPool:: "+request)
    type=request
    MetricDict={}
    for _l in MonitorList:
        MetricDict[_l]=[]
    pool=ThreadPoolExecutor(1)
    task=pool.submit(RunBenchmark, type)    #Start another thread to run benchmark
    cnt=0
    while(not task.done()):                 #Monitor CPU/MEM/IO while benchmarking
        #time.sleep(0.4)
        cnt+=1
        #print(cnt,time.time())
        stattmp=GetStatMetric()
        for _l in MonitorList:
            MetricDict[_l].append(stattmp[_l])
    BenchTime=task.result()
    if(cnt>1):          #remove the last one in list MetricDict[_l], since the last monitor data may be get after the bench finished
        cnt-=1
        for _l in MonitorList:
            MetricDict[_l].pop()
    MetricList=[]
    MetricList.append(str(cnt))
    for _l in MonitorList:
        MetricList.append(_l)
        for _x in MetricDict[_l]:
            MetricList.append(_x)
    MetricList.append(str(BenchTime))
    print("Bench "+type+" finished. ", len(MetricDict['CPUUSG']), cnt)
    return(MetricList)

if __name__ == '__main__':
    print("VPS agent running")
    time.sleep(15)
    socket.send_pyobj("vps started")
    msg=socket.recv_pyobj()
    ResList=RunBenchmarkPool(msg)
    socket.send_pyobj(ResList)
    time.sleep(2)
    # TODO: shutdown vps
    os.system('shutdown -P now')

