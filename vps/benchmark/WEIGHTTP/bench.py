import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        os.chdir('./benchmark/WEIGHTTP/')
        start_time = time.time()
        os.system('weighttp -n 10000 -c 10 -t 2 -k -H "User-Agent: foo" http://www-users.cs.umn.edu/~kauffman/4061/schedule.html')
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark WEIGHTTP: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark WEIGHTTP")
        return (10)
