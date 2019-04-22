import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        os.chdir('./benchmark/7ZBENCH2/')
        if(not os.path.exists('w7.iso')):
            os.system('wget http://www-users.cselabs.umn.edu/~wang8662/w7.iso -O w7.iso')
        start_time = time.time()
        os.system('7z x -ow7 w7.iso')
        os.system("7z a w7.7z w7/")
        os.system("rm w7.7z")
        os.system("rm -rf w7")
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark 7ZBENCH2: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark 7ZBENCH2")
        return (10)

