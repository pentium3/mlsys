#! /usr/bin/env python
# -*- coding: utf-8 -*-

# VPS side
import grpc
import sys
import os
pwd=os.path.join(os.getcwd(),"..")
sys.path.append(pwd)
pwd=os.path.join(os.getcwd(),"..","proto")
sys.path.append(pwd)
import time
from concurrent import futures
from proto import data_pb2, data_pb2_grpc
import psutil
import json
from concurrent.futures import ThreadPoolExecutor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '8080'

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
    print("received req for " + type + " == " + ans)
    return (ans)

def RunBenchmark(type):
    time.sleep(790)
    #TODO: Run real benchmarking
    print("Bench "+type+" finished")

class FormatData(data_pb2_grpc.FormatDataServicer):
    def sample(self, request, context):
        str = request.text
        return data_pb2.StrObj(text=str.upper())

    #Run benchmark and monitor CPU/MEM/IO at the same time
    def RunBenchmarkPool(self, request, context):
        type=request.text
        MetricDict={}
        for _l in MonitorList:
            MetricDict[_l]=[]
        pool=ThreadPoolExecutor(1)
        task=pool.submit(RunBenchmark, type)    #Start another thread to run benchmark
        cnt=0
        while(not task.done()):                 #Monitor CPU/MEM/IO while benchmarking
            time.sleep(1)
            cnt+=1
            for _l in MonitorList:
                MetricDict[_l].append(GetStatMetric(_l))
        MetricList=[]
        MetricList.append(str(cnt))
        for _l in MonitorList:
            MetricList.append(_l)
            for _x in MetricDict[_l]:
                MetricList.append(_x)
        return(data_pb2.ListObj(lstobj=MetricList))

def serve():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    data_pb2_grpc.add_FormatDataServicer_to_server(FormatData(), grpcServer)
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)

if __name__ == '__main__':
    serve()

