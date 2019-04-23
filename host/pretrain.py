#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Host side
import sys
import json
import os
import time
import xml.etree.ElementTree as XET
import zmq
import pickle


benchlist=['FFMPEG2', 'FFMPEG1', '7ZBENCH2']

class SearchSpace():
    def ReadCfgFile(self, CfgFile):
        f=open(CfgFile)
        self.CfgDict=json.load(f)
        self.CfgSet=list(self.CfgDict.keys())

    def SetVPSCfg(self, FileName, NewCfgDict):
        NewFileName = FileName.replace('.xml', '_new.xml')
        os.system('rm '+NewFileName)
        NewCPU=NewCfgDict['cpu']
        NewMEM=NewCfgDict['mem']
        NewHDD=NewCfgDict['hdd']
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

def RunBenchOnVPS(socket, BenchType):
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
    for _b in benchlist:
        TrainingSet = {}
        TrainingMon = {}
        for nc in cfgspace.CfgDict['cpu']:
            for nm in cfgspace.CfgDict['mem']:
                for nh in cfgspace.CfgDict['hdd']:
                    context = zmq.Context()
                    socket = context.socket(zmq.REP)
                    socket.bind("tcp://*:5555")
                    #Initialize VPS configuration
                    NewCfgDict={"cpu": nc, "mem": nm, "hdd": nh}
                    NewPrice=cfgspace.SetVPSCfg("vpstemplate.xml", NewCfgDict)
                    #wait for starting vps
                    os.system("virsh start ubuntu")
                    response = socket.recv_pyobj()
                    print(response)
                    #run benchmark on VPS
                    # NOT A BUG: only support 1 type of benchmark at one time
                    BenchTime, MetricDict=RunBenchOnVPS(socket, _b)
                    print('-------------------------------------------------')
                    print('Bench: ', _b, BenchTime, len(MetricDict['CPUUSG']))
                    print('price: ', NewPrice)
                    print('cfg:   ', NewCfgDict)
                    print('-------------------------------------------------')
                    os.system("virsh shutdown ubuntu")
                    while True:
                        runshell = os.popen('virsh list').read()
                        if(runshell.find('ubuntu')==-1):
                            break
                    Key=str([nc,nm,nh,_b])
                    MetricDict['BenchTime']=BenchTime
                    MetricDict['Price']=NewPrice
                    TrainingSet[Key]=BenchTime*BenchTime*NewPrice
                    TrainingMon[Key]=MetricDict
                    time.sleep(3)
        savedat=_b+'_sec.pkl'
        fw=open(savedat, 'wb')
        pickle.dump(TrainingSet, fw, pickle.HIGHEST_PROTOCOL)
        fw.close()
        savemondat=_b+'_mon.pkl'
        fw1=open(savemondat, 'wb')
        pickle.dump(TrainingMon, fw1, pickle.HIGHEST_PROTOCOL)
        fw1.close()
        print(TrainingSet)