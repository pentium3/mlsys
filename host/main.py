#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Host side
import sys
import json
import os
import time
import xml.etree.ElementTree as XET
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

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
        NewCPU=list(self.CfgDict['cpu'].keys())[NewCPUidx]
        NewMEM=list(self.CfgDict['mem'].keys())[NewMEMidx]
        NewHDD=list(self.CfgDict['hdd'].keys())[NewHDDidx]
        NewPrice=self.CfgDict['cpu'][NewCPU]+self.CfgDict['mem'][NewMEM]+self.CfgDict['hdd'][NewHDD]
        print('setcfg: ', NewCPU, NewMEM, NewHDD, NewPrice)
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
        return(NewPrice)

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
    #init
    cfgspace=SearchSpace()
    cfgspace.ReadCfgFile('vpscfg.json')
    print('vpscfg: ', cfgspace.CfgDict)
    #Initialize VPS configuration
    NewCfgDict={"cpu": 5, "mem": 5, "hdd": 2}
    NewPrice=cfgspace.SetVPSCfg("vpstemplate.xml", NewCfgDict)
    print('setcfg: price==', NewPrice)

    #wait for starting vps
    #os.system("virsh start ubuntu")
    response = socket.recv_pyobj()
    print(response)

    #run benchmark on VPS
    # BUG: only support 1 type of benchmark at one time
    BenchTime, MetricDict=RunBenchOnVPS("MD5CPU")
    print('bench: ', BenchTime, len(MetricDict['CPUUSG']))

    #TODO: ML model to choose new configuration
    time.sleep(1)

    #Change VPS configuration
    NewCfgDict={"cpu": 0, "mem": 0, "hdd": 0}
    NewPrice=cfgspace.SetVPSCfg("vpstemplate.xml", NewCfgDict)
    print('setcfg: price==', NewPrice)

