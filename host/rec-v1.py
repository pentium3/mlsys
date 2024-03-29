import pickle
import os
import re
import pandas as pd
from surprise import SVD, SVDpp, NMF
from surprise import Dataset, accuracy
from surprise import evaluate, print_perf, Reader
from surprise.model_selection import GridSearchCV
from surprise.model_selection import train_test_split

benchlist=['MYSQL_1', 'MYSQL_2', 'MYSQL_3', 'MYSQL_4', 'MYSQL', 'MD5CPU', '7ZBENCH', 'CNN', 'GAN', 'FFMPEG', '7ZBENCH2', 'FFMPEG1', 'FFMPEG2', 'DISKIO']
# whole set
predict_bench='DISKIO'
# testing set
benchlist1=benchlist.copy()
benchlist1.remove(predict_bench)
# training dataset
print("train", benchlist1)
print("test ", predict_bench)
print("whole", benchlist)
MAXTIME=50    #for normalization
MAXCOST=300    #for normalization

vpsset={}
f=pickle.load(open('MYSQL_mon.pkl','rb'))
for _v in list(f.keys()):
    vps=_v.replace('MYSQL','')
    vpsset[vps]=len(vpsset)
    #print(vpsset[vps],vps)

def pkl2dat(benchlist, filename):
    os.system('rm '+filename)
    ff = open(filename,'w')
    for benno,_b in enumerate(benchlist):
        f=pickle.load(open(_b+'_mon.pkl','rb'))
        for _v in list(f.keys()):
            if(_v.find(_b)!=-1):
                vpsst=_v.replace(_b,'')
                vpsno=vpsset[_v.replace(_b,'')]
                vpstm=f[_v]['BenchTime']
                vpspr=f[_v]['Price']
                vpscpumon=f[_v]['CPUUSG']
                vpsmemmon=f[_v]['MEMUSG']
                vpssc=(vpstm/MAXTIME)#*(vpstm/MAXTIME)*(vpspr*MAXCOST)
                vpshdrmon=f[_v]['IORRAT']
                vpshdwmon=f[_v]['IOWRAT']
                ff.write(str(_b) + " " + str(vpsno) + " " + str(vpssc) + " 1\n")
                #print(_b, vpsst, vpstm, vpspr)
                #print(vpscpumon, vpsmemmon, vpshdrmon, vpshdwmon)
    ff.close()

def pkl2testdat(benchlist, filename, refcfglist, initval):
    os.system('rm '+filename)
    ff = open(filename,'w')
    for benno,_b in enumerate(benchlist):
        f=pickle.load(open(_b+'_mon.pkl','rb'))
        for _v in list(f.keys()):
            if(_v.find(_b)!=-1):
                vpsst=_v.replace(_b,'')
                vpsno=vpsset[_v.replace(_b,'')]
                vpstm=f[_v]['BenchTime']
                vpspr=f[_v]['Price']
                vpscpumon=f[_v]['CPUUSG']
                vpsmemmon=f[_v]['MEMUSG']
                vpssc=(vpstm/MAXTIME)#*(vpstm/MAXTIME)*(vpspr*MAXCOST)
                vpshdrmon=f[_v]['IORRAT']
                vpshdwmon=f[_v]['IOWRAT']
                if(vpsno in refcfglist):
                    ff.write(str(_b) + " " + str(vpsno) + " " + str(vpssc) + " 1\n")
                #else:
                #    ff.write(str(_b) + " " + str(vpsno) + " " + str(initval) + "\n")
                #print(_b, vpsst, vpstm, vpspr)
                #print(vpscpumon, vpsmemmon, vpshdrmon, vpshdwmon)
    ff.close()

def txt2list(filename):
    ff = open(filename,'r')
    res=[]
    for i in ff.readlines():
        _l=i.replace('\n','').split(' ')
        res.append((_l[0], _l[1], _l[2]))
    return(res)

# numselected must be positive integer
# file content must have repeated structure: "appname vpsid time 1\n"
def selectVPS(filename, numselected): 
    fd = open(filename)
    lines = fd.readlines()
    fd.close()
    num_apps = 0
    num_vpss = 0
    list_squaresum = []
    list_sum = []
    for line in lines:
        match = re.search(r'^.*\s(\d+)\s(\d+\.\d+)\s1\s$', line)
        if match: 
            curr_vpsid_str = match.group(1)
            curr_time_str = match.group(2)
            curr_vpsid = int(curr_vpsid_str)
            curr_time = float(curr_time_str)
            
            # init case
            if curr_vpsid == 0: 
                num_apps = num_apps + 1
                pass
            if curr_vpsid >= num_vpss: 
                num_vpss = num_vpss + 1
                pass
            
            if num_apps == 1: 
                list_squaresum.append(curr_time*curr_time)
                list_sum.append(curr_time)
                pass
            else: 
                list_squaresum[curr_vpsid] = list_squaresum[curr_vpsid] + curr_time*curr_time
                list_sum[curr_vpsid] = list_sum[curr_vpsid] + curr_time
                pass
            pass
        else: 
            print "re not match! "
            return [-1]*numselected
        pass
    if numselected > num_vpss: 
        print "no enough vpss"
        return [-1]*numselected
    
    print num_apps, num_vpss
    
    # calculate the variance
    list_var = []
    for index in range(num_vpss): 
        temp = list_squaresum[index]/num_apps - (list_sum[index]/num_apps)**2
        list_var.append((temp, index))
        pass
    list_var.sort(reverse = True)
    print list_var
    
    ret_list = []
    for index in range(numselected): 
        ret_list.append(list_var[index][1])
        pass
    return ret_list
    pass


pkl2dat(benchlist, 'pretrain.txt')
pkl2dat([predict_bench], 'testorig.txt')
pkl2dat(benchlist1, 'train.txt')
selected_vpsids = selectVPS("train.txt", 4)
pkl2testdat([predict_bench], 'test.txt', selected_vpsids, 0)
os.system('rm tmp.txt')
os.system('cat train.txt test.txt > tmp.txt')

# print("")
# print("RMSE on cross validation on whole dataset")
# print("***************************************************************************")
# fp=os.path.expanduser('pretrain.txt')
# fr=Reader(line_format='user item rating timestamp',sep=' ')
# # user: benno | item: vpsno | rating: vpssc
# data=Dataset.load_from_file(fp, reader=fr)
# param_grid = {'n_epochs': [200, 150, 100], 
#               'lr_bu': [0.002, 0.005, 0.008, 0.01, 0.02], 
#               'lr_bi': [0.002, 0.005, 0.008, 0.01, 0.02], 
#               'lr_pu': [0.002, 0.005, 0.008, 0.01, 0.02], 
#               'lr_qi': [0.002, 0.005, 0.008, 0.01, 0.02], 
#               'reg_bu': [0.02, 0.04, 0.06],
#               'reg_bi': [0.02, 0.04, 0.06],
#               'reg_pu': [0.02, 0.04, 0.06],
#               'reg_qi': [0.02, 0.04, 0.06],
#               }
# gs = GridSearchCV(SVD, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
# gs.fit(data)
# print(gs.best_score)
# print(gs.best_params)

# fp=os.path.expanduser('pretrain.txt')
# fr=Reader(line_format='user item rating timestamp',sep=' ')
# # user: benno | item: vpsno | rating: vpssc
# data=Dataset.load_from_file(fp, reader=fr)
# param_grid = {'n_epochs': [30, 40, 50, 60, 70], 
#               'lr_bu': [0.002, 0.005, 0.007, 0.01, 0.02], 
#               'lr_bi': [0.005, 0.002, 0.007, 0.01, 0.02],
#               'reg_pu': [0.06, 0.04, 0.08],
#               'reg_qi': [0.06, 0.04, 0.08],
#               'reg_bu': [0.02, 0.04],
#               'reg_bi': [0.02, 0.04],
#               'init_high': [1, 5, 7, 10]
#               }
# gs = GridSearchCV(NMF, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
# gs.fit(data)
# print(gs.best_score)
# print(gs.best_params)
# ## https://surprise.readthedocs.io/en/stable/matrix_factorization.html
# print("**************************************************************************")

print("")
print("Top-K accuracy on splited testing set with 2 ref configuration")
print("the ref configurations are choosen randomly")
print("***************************************************************************")
fr=Reader(line_format='user item rating timestamp',sep=' ')
fp=os.path.expanduser('tmp.txt')
dtmp=Dataset.load_from_file(fp, reader=fr)
param_grid = {'n_epochs': [70, 100, 150, 200], 
             'lr_all': [0.002, 0.005, 0.008, 0.01, 0.02], 
             'reg_all': [0.04, 0.06, 0.02, 0.08, 0.1]}
gs = GridSearchCV(SVD, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
gs.fit(dtmp)
print(gs.best_score)
galgo=gs.best_estimator['rmse']
print(type(galgo))
galgo.fit(dtmp.build_full_trainset())
reslist=[]
for i in range(75):
    pred=galgo.predict(predict_bench,str(i))
    reslist.append((pred.uid, pred.iid, pred.est))
ressort=sorted(reslist, key= lambda k:float(k[2]))
print('predict: ------------------------------------------------------------------')
print(ressort)
print([r[1] for r in ressort[:10]])
origlist=txt2list('testorig.txt')
origsort=sorted(origlist, key= lambda k:float(k[2]))
print('original: -----------------------------------------------------------------')
print(origsort)
print([r[1] for r in origsort[:10]])
print("***************************************************************************")


