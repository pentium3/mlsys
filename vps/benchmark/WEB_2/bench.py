import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        start_time = time.time()
        os.chdir('./benchmark/WEB_2/')
        os.system('./build.sh')
        os.system('./htstress -n 100000 -c 100 -t 4 www.google.com')
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark htstress: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark htstress")
        return (10)
