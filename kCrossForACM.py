import shutil,os,sys,TestingForACM
from TestingForACM import *




# input:
# 1- Data dir
# 2- num of k
# 3- num of checks
# 4- num of elements to compare
def main():
    inDir = sys.argv[1]
    k = int(sys.argv[2]) 
    numOfChecks = int(sys.argv[3])
    numOfElem = int(sys.argv[4])

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
        ACM = AutoCompModule('DB_'+str((i+1)))
        ACM.learn(inDir)
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
            shutil.move(file,inDir)
    for a in totRes:
        a = round(a/k,2)
    print (totRes)


if __name__ == '__main__':
    main()
