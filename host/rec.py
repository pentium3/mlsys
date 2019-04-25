import pickle
import os
import pandas as pd
from surprise import SVD, SVDpp, NMF
from surprise import Dataset, accuracy
from surprise import evaluate, print_perf, Reader
from surprise.model_selection import GridSearchCV
from surprise.model_selection import train_test_split

MAXTIME=50    #for normalization
MAXCOST=25    #for normalization

vpsset={}
f=pickle.load(open('MYSQL_mon.pkl','rb'))
for _v in list(f.keys()):
    vps=_v.replace('MYSQL','')
    vpsset[vps]=len(vpsset)
    print(vpsset[vps],vps)

def pkl2dat(benchlist, filename):
    os.system('rm '+filename)
    ff = open(filename,'w')
    for benno,_b in enumerate(benchlist):
        f=pickle.load(open(_b+'_mon.pkl','rb'))
        for _v in list(f.keys()):
            if(_v.find(_b)!=-1):
                vpsst=_v.replace(_b,'')
                vpsno=vpsset[_v.replace(_b,'')]
                vpstm=f[_v]['BenchTime']    #total time
                vpspr=f[_v]['Price']        #cost per hour
                vpscpumon=f[_v]['CPUUSG']
                vpsmemmon=f[_v]['MEMUSG']
                vpssc=(vpspr/MAXCOST)*(vpstm/MAXTIME)#*(vpspr*MAXCOST)
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
                vpssc=(vpspr/MAXCOST)*(vpstm/MAXTIME)#*(vpspr*MAXCOST)
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

def topsim(l1, l2):
    ll=len(l1)
    ans=0
    for _l in l1:
        if(_l in l2):
            ans+=1
    return(ans)

benchlist=['MYSQL_1', 'MYSQL_2', 'MYSQL_3', 'MYSQL_4', 'MYSQL', 'MD5CPU', '7ZBENCH', 'CNN', 'GAN', 'FFMPEG', '7ZBENCH2', 'FFMPEG1', 'FFMPEG2', 'DISKIO']
# whole set


pkl2dat(benchlist, 'pretrain.txt')
# print("")
# print("RMSE on cross validation on whole dataset")
# print("***************************************************************************")
# fp=os.path.expanduser('pretrain.txt')
# fr=Reader(line_format='user item rating timestamp',sep=' ')
# # user: benno | item: vpsno | rating: vpssc
# data=Dataset.load_from_file(fp, reader=fr)
# param_grid = {'n_epochs': [200, 150, 300, 250], 
#               'lr_all': [0.03, 0.005, 0.04, 0.01, 0.05], 
#               'reg_all': [0.02, 0.04, 0.01],
#               }
# gs = GridSearchCV(SVD, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
# gs.fit(data)
# print(gs.best_score)
# print(gs.best_params)

# fp=os.path.expanduser('pretrain.txt')
# fr=Reader(line_format='user item rating timestamp',sep=' ')
# # user: benno | item: vpsno | rating: vpssc
# data=Dataset.load_from_file(fp, reader=fr)
# param_grid = {'n_epochs': [30, 50, 70, 100], 
#               'lr_bu': [0.007, 0.01, 0.02], 
#               'lr_bi': [0.007, 0.01, 0.02],
#               'reg_pu': [0.06, 0.04, 0.08],
#               'reg_qi': [0.06, 0.04, 0.08],
#               'reg_bu': [0.02, 0.04, 0.06],
#               'reg_bi': [0.02, 0.04, 0.06]
#               }
# gf = GridSearchCV(NMF, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
# gf.fit(data)
# print(gf.best_score)
# print(gf.best_params)
# ## https://surprise.readthedocs.io/en/stable/matrix_factorization.html
# print("**************************************************************************")


#predict_bench='DISKIO'
for predict_bench in benchlist:
    print("")
    print("Top-K accuracy on splited testing set with 9 ref configuration")
    print("the ref configurations are choosen randomly")
    print("***************************************************************************")
    # testing set
    benchlist1=benchlist.copy()
    benchlist1.remove(predict_bench)
    # training dataset
    print("train", benchlist1)
    print("test ", predict_bench)
    print("whole", benchlist)

    pkl2dat([predict_bench], 'testorig.txt')
    pkl2dat(benchlist1, 'train.txt')
    pkl2testdat([predict_bench], 'test.txt', [36, 37, 38, 72, 73, 74, 0, 1, 2], 0)
    os.system('rm tmp.txt')
    os.system('cat train.txt test.txt > tmp.txt')

    fr=Reader(line_format='user item rating timestamp',sep=' ')
    fp=os.path.expanduser('tmp.txt')
    dtmp=Dataset.load_from_file(fp, reader=fr)
    # param_grid = {'n_epochs': [200, 150, 300, 250, 400], 
    #               'lr_all': [0.03, 0.005, 0.04, 0.01, 0.05], 
    #               'reg_all': [0.02, 0.04, 0.01],
    #               }
    param_grid = {'n_epochs': [30, 50, 70, 100], 
                'lr_bu': [0.007, 0.01, 0.02], 
                'lr_bi': [0.007, 0.01, 0.02],
                'reg_pu': [0.06, 0.04, 0.08],
                'reg_qi': [0.06, 0.04, 0.08],
                'reg_bu': [0.02, 0.04, 0.06],
                'reg_bi': [0.02, 0.04, 0.06]
                }
    gs= GridSearchCV(NMF, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
    #gs = GridSearchCV(SVD, param_grid, measures=['RMSE', 'MAE'], n_jobs=-1)
    gs.fit(dtmp)
    print(gs.best_score)
    print(gs.best_params)
    gsalgo=gs.best_estimator['rmse']
    gsalgo.fit(dtmp.build_full_trainset())
    reslist=[]
    for i in range(75):
        pred=gsalgo.predict(predict_bench,str(i))
        reslist.append((pred.uid, pred.iid, pred.est))
    ressort=sorted(reslist, key= lambda k:float(k[2]))
    # print(ressort)
    predtop=[r[1] for r in ressort[:10]]
    origlist=txt2list('testorig.txt')
    origsort=sorted(origlist, key= lambda k:float(k[2]))
    # print(origsort)
    origtop=[r[1] for r in origsort[:10]]
    topacc=topsim(predtop, origtop)
    print(topacc, predtop, origtop)
    print(ressort[0], origsort[0], ressort[1], origsort[1])
    print("***************************************************************************")


