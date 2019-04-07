#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Host side
import grpc
import sys
import os
pwd=os.path.join(os.getcwd(),"..")
sys.path.append(pwd)
pwd=os.path.join(os.getcwd(),"..","proto")
sys.path.append(pwd)
from proto import data_pb2, data_pb2_grpc

_HOST = 'localhost'
_PORT = '8080'

def run():
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = data_pb2_grpc.FormatDataStub(channel=conn)
    response = client.GetStatMetric(data_pb2.Data(text='NTBYTE'))
    print("received: " + response.text)

if __name__ == '__main__':
    run()