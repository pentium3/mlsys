import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        start_time = time.time()
        os.chdir('./benchmark/DISKIO/')
        os.system('rm -f BenchTmp')
        os.system('rm -f BenchTmp2')
        cmd = "dd if=/dev/zero of=./BenchTmp bs=8k count=250000 oflag=direct"
        os.system(cmd)
        # Test Read ability: 2GB file with 8K blocks. ignore memory cache
        cmd = "dd if=./BenchTmp of=./BenchTmp2 bs=8k count=250000 oflag=direct"
        os.system(cmd)
        # Test Write ability: 2GB file with 8K blocks. ignore memory cache
        cmd = "rm -f BenchTmp"
        os.system(cmd)
        cmd = "rm -f BenchTmp2"
        os.system(cmd)
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print(self.total_ptime)
        print("This is Benchmark DISKIO: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark DISKIO")
        return (10)

