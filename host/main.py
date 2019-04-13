#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Host side
import grpc
import sys
import json
import os
import time
import xml.etree.ElementTree as XET
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.122.28:5555")

context2=zmq.Context()
socket2=context2.socket(zmq.REP)
socket2.bind("tcp://*:5556")

class SearchSpace():
    def ReadCfgFile(self, CfgFile):
        f=open(CfgFile)
        self.CfgDict=json.load(f)
        self.CfgSet=list(self.CfgDict.keys())

    def SetVPSCfg(self, FileName, NewCfgDict):
        NewFileName = FileName.replace('.xml', '_new.xml')
        os.system('rm '+NewFileName)
        NewCPUidx=NewCfgDict['cpu']
        NewMEMidx=NewCfgDict['mem']
        NewHDDidx=NewCfgDict['hdd']
        CPUlen=len(self.CfgDict['cpu'])
        MEMlen=len(self.CfgDict['mem'])
        HDDlen=len(self.CfgDict['hdd'])
        if(NewCPUidx>=CPUlen or NewMEMidx>=MEMlen or NewHDDidx>=HDDlen):
            return(-1)
        NewCPU=self.CfgDict['cpu'][NewCPUidx]
        NewMEM=self.CfgDict['mem'][NewMEMidx]
        NewHDD=self.CfgDict['hdd'][NewHDDidx]
        print('setcfg: ', NewCPU, NewMEM, NewHDD)
        tree = XET.parse(FileName)
        root=tree.getroot()
        vcpu=root.find('vcpu')
        cores=root.find('cpu').find('topology')
        memory=root.find('memory')
        currentmemory=root.find('currentMemory')
        disk=root.find('devices').find('disk').find('source')
        vcpu.text=NewCPU
        cores.attrib['cores']=NewCPU
        memory.text=NewMEM
        currentmemory.text=NewMEM
        disk.attrib['file']=NewHDD
        tree.write(NewFileName)
        os.system('virsh define '+NewFileName)
        return(1)

def RunBenchOnVPS(BenchType):
    socket.send_pyobj(BenchType)
    response=socket.recv_pyobj()
    MetricList=response
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
    os.system("virsh start ubuntu")
    response = socket2.recv_pyobj()
    print(response)

    #init
    cfgspace=SearchSpace()
    cfgspace.ReadCfgFile('vpscfg.json')
    print('vpscfg: ', cfgspace.CfgDict)

    #run benchmark on VPS
    # BUG: only support 1 type of benchmark at one time
    BenchTime, MetricDict=RunBenchOnVPS("CNN")
    print('bench: ', BenchTime, len(MetricDict['cpu']))

    #TODO: ML model to choose new configuration
    time.sleep(1)

    #Change VPS configuration
    NewCfgDict={"cpu": 3, "mem": 3, "hdd": 2}
    res=cfgspace.SetVPSCfg("vpstemplate.xml", NewCfgDict)
    print('setcfg: ', res)

