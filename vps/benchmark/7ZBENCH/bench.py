import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        os.chdir('./benchmark/7ZBENCH/')
        if(not os.path.exists('w98.iso')):
            os.system('wget http://www-users.cselabs.umn.edu/~wang8662/w98.iso -O w98.iso')
        start_time = time.time()
        os.system('7z x -ow98 w98.iso')
        os.system("7z a w98.7z w98/")
        os.system("rm w98.7z")
        os.system("rm -rf w98")
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark 7ZBENCH: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark 7ZBENCH")
        return (10)

