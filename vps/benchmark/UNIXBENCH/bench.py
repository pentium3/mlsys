import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        start_time = time.time()
        os.chdir('./benchmark/UNIXBENCH/UnixBench/')
        os.system('rm -f BenchRes')
        cmd="./Run -i 1 >> BenchRes"
        os.system(cmd)
        runshell=os.popen('cat BenchRes | grep Score').read()
        runshell=runshell.replace('System Benchmarks Index Score                                        ','')
        runshell=float(runshell)    #UnixBench Score
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print(runshell,type(runshell),self.total_ptime)
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark UNIXBENCH")
        return (10)

