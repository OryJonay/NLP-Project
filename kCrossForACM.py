import shutil, os ,sys, TestingForACM
from TestingForACM import *
from pymongo import Connection
from ACM import ACM
from Experiments import *

connect = 'mongodb://project:project1234@yeda.cs.technion.ac.il/'

# input:
# 1- Data dir
# 2- num of k
# 3- num of checks
# 4- num of elements to compare

def kCrossFix(data,k): 
    filesAmount = len(os.listdir(data))
    groupSize=int(filesAmount/k)
    i=0
    folds = {n:({},{}) for n in range(1,k+1)}
    while i < k:
        j=1
        while j <= groupSize:
            filenum = (groupSize*i) + j
            shutil.move(data+'/'+str(filenum)+'.txt','Test')
            j+=1
        
        acm = ACM('db'+str((i+1)))
        acm.dropDicts('db'+str(i+1))
        acm.learn(data)
        
        folds[i+1] = (weight_expr(acm,'Test') , buff_size_expr(acm,'Test'))
        
        i+=1
        
        for file in os.listdir('Test'):
            shutil.move('Test/'+file,data)
    
    weight_res = [folds[fold][0] for fold in folds]
    buff_size_res = [folds[fold][1] for fold in folds]
    tot_w_res = {}
    for key in weight_res[0]:
        for res in weight_res:
            tot_w_res[key] += res[key]
    tot_b_res = {}
    for key in buff_size_res[0]:
        for res in buff_size_res:
            tot_b_res[key] += res[key]
    
    tot_w_res = {key:float(tot_w_res[key]/k) for key in tot_w_res}
    tot_b_res = {key:float(tot_b_res[key]/k) for key in tot_b_res}
    
    return [tot_w_res[i] for i in sorted(tot_w_res)] , [tot_b_res[i] for i in sorted(tot_b_res)]

def learnAll(inDir,k,type):
    filesAmount = len(os.listdir(inDir))
    groupSize=int(filesAmount/k)
    i=0
    while i < k:
        j=1
        while j <= groupSize:
            filenum = (groupSize*i) + j
            shutil.move(inDir+'/'+str(filenum)+'.txt','Test')
            j+=1
        if type == 'LDA':
            acm = LDA('db'+str((i+1)))
            acm.dropDicts('db'+str((i+1)))
            acm.learn(inDir)
        else:
            acm = AutoCompModule('db'+str((i+1)))
            acm.dropDicts('db'+str((i+1)))
            acm.learn(inDir)
        i+=1
        for file in os.listdir('Test'):
            shutil.move('Test/'+file,inDir)
    print ('Done learning')


def checkLDA(inDir,k):
    filesAmount = len(os.listdir(inDir))
    groupSize=int(filesAmount/k)
    i=0
    while i < k:
        j=1
        while j <= groupSize:
            filenum = (groupSize*i) + j
            shutil.move(inDir+'/'+str(filenum)+'.txt','Test')
            j+=1
        lda = LDA('db'+str((i+1)))
        lda.learn(inDir)
        i+=1
        for file in os.listdir('Test'):
            shutil.move('Test/'+file,inDir)
    print ("Done learning")

def runTest(data,k):
    
    weight_g , buff_size_g = kCrossFix(data, k) 
    import numpy as np
    import matplotlib.pyplot as plt

    plt.title(str(k)+'-Cross validation')
    plt.xlabel('Weight of trigram')
    plt.ylabel('Success rate')
    plt.plot(range(10,101,10),weight_g,'k')
    plt.savefig(str(k)+'Cross-weights.png')
    plt.title(str(k)+'-Cross validation')
    plt.xlabel('Size of buffer')
    plt.ylabel('Success rate')
    plt.plot(range(15,121,15),buff_size_g,'k')
    plt.savefig(str(k)+'Cross-buffer_size.png')

def main():
    if sys.argv[1] == 'LDA':
        checkLDA(sys.argv[2],int(sys.argv[3]))
    else:
        runTest(sys.argv[1], int(sys.argv[2]))
                                                                            
    

if __name__ == '__main__':
    main()
