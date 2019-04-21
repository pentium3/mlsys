import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        os.chdir('./benchmark/FFMPEG/')
        if(not os.path.exists('v.mp4')):
            os.system('wget http://www-users.cselabs.umn.edu/~wang8662/v.mp4 -O v.mp4')
        start_time = time.time()
        os.system('ffmpeg -i v.mp4 -c:v libx264 -crf 44 vo.kmv')
        os.system("rm vo.avi")
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark FFMPEG: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark FFMPEG")
        return (10)
