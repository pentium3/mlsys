import numpy as np
import os
import time
from hashlib import md5
from string import ascii_letters,digits
from itertools import permutations

class Bench(object):
    total_ptime = 0

    def decrypt_md5(self, md5_value):
        all_letters = ascii_letters + digits + '.,;'
        if len(md5_value) != 32:
            print('error')
            return
        md5_value = md5_value.lower()
        for k in range(5, 10):
            print(k, '.', end='')
            for item in permutations(all_letters, k):
                item = ''.join(item)
                if md5(item.encode()).hexdigest() == md5_value:
                    return item

    def Run(self, ):
        start_time = time.time()
        md5_value = 'ff77bed3fd3bebe8a3bc1210d3297449'
        result = self.decrypt_md5(md5_value)
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark MD5CPU: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark MD5CPU")
        return (10)

