#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Host side
import grpc
import sys
import json
import os
pwd=os.path.join(os.getcwd(),"..")
sys.path.append(pwd)
pwd=os.path.join(os.getcwd(),"..","proto")
sys.path.append(pwd)
from proto import data_pb2, data_pb2_grpc

_HOST = 'localhost'
_PORT = '8080'

class SearchSpace():
    def ReadCfgFile(self, CfgFile):
        f=open(CfgFile)
        self.CfgDict=json.load(f)
        self.CfgSet=list(self.CfgDict.keys())

def RunBenchOnVPS(BenchType):
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = data_pb2_grpc.FormatDataStub(channel=conn)
    response = client.RunBenchmarkPool(data_pb2.StrObj(text=BenchType))
    MetricList=response.lstobj
    BenchTime=int(MetricList[-1])
    cnt=int(MetricList[0])
    NumofMetrics=int((len(MetricList)-1)/(cnt+1))
    NumofRecords=cnt
    MetricDict={}
    for i in range(NumofMetrics):
        st=1+i*(NumofRecords+1)
        tmp=MetricList[st]
        MetricDict[tmp]=[]
        for j in range(st+1,st+NumofRecords+1):
            MetricDict[tmp].append(MetricList[j])
    return (BenchTime, MetricDict)

if __name__ == '__main__':
    BenchTime, MetricDict=RunBenchOnVPS("CNN")       #Host is blocked until benchmark finished
    print(BenchTime, MetricDict)