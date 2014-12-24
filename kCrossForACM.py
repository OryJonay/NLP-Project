import shutil,os,sys,TestingForACM
from TestingForACM import *
from pymongo import Connection
from ACM_LDA import ACM_LDA as LDA

connect = 'mongodb://project:project1234@yeda.cs.technion.ac.il/'

# input:
# 1- Data dir
# 2- num of k
# 3- num of checks
# 4- num of elements to compare

def kCrossFix(data,k,checks,elements=5,DBexists=False): 
    numOfChecks = int(checks)
    numOfElem = int(elements)

    filesAmount = len(os.listdir(inDir))
    groupSize=int(filesAmount/k)
    i=0
    totRes = [0,0,0,0,0]
    while i < k:
        j=1
        while j <= groupSize:
            filenum = (groupSize*i) + j
            shutil.move(inDir+'/'+str(filenum)+'.txt','Test')
            j+=1
        ACM = AutoCompModule('db'+str((i+1)))
        if not DBexists:
            ACM.dropDicts('db'+str((i+1)))
            ACM.learn(inDir)
        #Mallet
        #ACM.addMalletInfoToDB()
        print("iter num:"+str(i+1)+" checking every: "+str(numOfChecks))
        (s1,s2) = simpleTest(ACM,'Test',numOfChecks)
        (p1,p2) = probTest(ACM,'Test',numOfChecks)
        imp = impSimTest(ACM,'Test',numOfChecks,numOfElem)
        print("simple test result:",round(s1*100,2),"%", round(s2*100,2),"%",end = ' ')
        print("prob test result:",round(p1*100,2),"% ",round(p2*100,2),"%")
        print("improved simple test result:",round(imp*100,2),"%")
        i+=1
        totRes[0] += round(s1*100,2)
        totRes[1] += round(s2*100,2)
        totRes[2] += round(p1*100,2)
        totRes[3] += round(p2*100,2)
        totRes[4] += round(imp*100,2)
        for file in os.listdir('Test'):
            shutil.move('Test/'+file,inDir)
    for a in totRes:
        a = round(a/k,2)
    return totRes

SB='simple_bigram'
ST='simple_trigram'
PB='prob_bigram'
PT='prob_trigram'
IS='improv_simple'

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


def runTest(data,k,maxChecks=5,elements=5):
    tests = [SB,ST,PB,PT,IS]
    results = {test:[] for test in tests}
    DBexists=False
    import numpy as np
    for checks in np.arange(1,maxChecks+1):
        res = kCrossFix(data, k, checks, elements, DBexists)
        results[SB].append(res[0]/100)
        results[ST].append(res[1]/100)
        results[PB].append(res[2]/100)
        results[PT].append(res[3]/100)
        results[IS].append(res[4]/100)
        DBexists = True
    import matplotlib.pyplot as plt
    x = np.arange(1,maxChecks+1)
    plt.title(str(k)+'-Cross validation')
    plt.xlabel('Number of words before completing')
    plt.ylabel('Success rate')
    plt.plot(x,results[SB],'b:',label=SB,linewidth=4)
    plt.plot(x,results[ST],'r:',label=ST,linewidth=4)
    plt.plot(x,results[PB],'g:',label=PB,linewidth=4)
    plt.plot(x,results[PT],'c:',label=PT,linewidth=4)
    plt.plot(x,results[IS],'k:',label=IS,linewidth=4)
    plt.legend(loc='best', shadow=False, fontsize='medium')
    plt.savefig(str(k)+'Cross.png')

def main():
    if sys.argv[1] == 'LDA':
        checkLDA(sys.argv[2],int(sys.argv[3]))
    else:
        runTest(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
                                                                            
    

if __name__ == '__main__':
    main()
