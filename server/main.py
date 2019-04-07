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

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '8080'

class FormatData(data_pb2_grpc.FormatDataServicer):
    def sample(self, request, context):
        str = request.text
        return data_pb2.Data(text=str.upper())

    def GetStatMetric(self, request, context):
        type=request.text
        ans=""
        if(type=="CPUUSG"):
            ans=str(psutil.cpu_percent(interval=1,percpu=False))
        elif(type=="MEMTOT"):
            ans=str(psutil.virtual_memory().total)
        elif(type=="MEMUSG"):
            ans=str(psutil.virtual_memory().percent)
        elif(type=="IOBYTE"):
            ans=str(psutil.disk_io_counters())	    #total HDD I/O amount in Bytes
        elif(type=="NTBYTE"):
            ans=str(psutil.net_io_counters())		#total network I/O amount in Bytes
        print("received req for " + type + " == " + ans)
        return data_pb2.Data(text=ans)

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