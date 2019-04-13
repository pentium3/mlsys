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

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

context2=zmq.Context()
socket2=context2.socket(zmq.REP)
socket2.bind("tcp://192.168.122.1:5556")

MonitorList=['CPUUSG', 'MEMUSG', 'IOBYTE']

def GetStatMetric(type):
    ans=""
    if(type=="CPUUSG"):
        ans=str(psutil.cpu_percent(interval=1,percpu=False))
    elif(type=="MEMTOT"):
        ans=str(psutil.virtual_memory().total)
    elif(type=="MEMUSG"):
        ans=str(psutil.virtual_memory().percent)
    elif(type=="IOBYTE"):
        ans=str(psutil.disk_io_counters())	    #total HDD I/O amount in Bytes
    #print("received req for " + type + " == " + ans)
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
        time.sleep(0.4)
        cnt+=1
        #print(cnt,time.time())
        for _l in MonitorList:
            MetricDict[_l].append(GetStatMetric(_l))
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
    socket2.send_pyobj("started")
    while True:
        msg=socket.recv_pyobj()
        ResList=RunBenchmarkPool(msg)
        socket.send_pyobj(ResList)

