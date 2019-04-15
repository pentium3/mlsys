import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        start_time = time.time()
        os.chdir('./benchmark/7ZBENCH/UnixBench/')
        os.system('rm -f BenchRes')
        cmd="7z b >> BenchRes"
        os.system(cmd)
        runshell=os.popen('cat BenchRes').read()
        cmd = "rm BenchRes"
        os.system(cmd)
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print(runshell,type(runshell),self.total_ptime)
        print("This is Benchmark 7ZBENCH: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark 7ZBENCH")
        return (10)

