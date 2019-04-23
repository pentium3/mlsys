import numpy as np
import os
import time

class Bench(object):
    total_ptime = 0

    def Run(self, ):
        start_time = time.time()
        os.chdir('./benchmark/MYSQL_4/')
        os.system('sysbench oltp_read_write --db-driver=mysql --table-size=5000000  --mysql-host=localhost --mysql-db=hive --mysql-user=root --mysql-password=123456 prepare')
        os.system('sysbench oltp_read_write --db-driver=mysql --table-size=5000000 --mysql-db=hive --mysql-user=root --mysql-password=123456 --max-requests=0 --num-threads=16 --oltp-reconnect-mode=random run')
        os.system('sysbench oltp_read_write --db-driver=mysql --table-size=5000000  --mysql-host=localhost --mysql-db=hive --mysql-user=root --mysql-password=123456 cleanup')
        end_time = time.time()
        self.total_ptime = (int)(end_time - start_time)
        print("This is Benchmark MYSQL: "+(str)(self.total_ptime))
        return (self.total_ptime)

    def sampleRun(self,):
        print("This is Benchmark MYSQL")
        return (10)

if __name__ == '__main__':
    mybench = Bench()
    print(mybench.Run())

