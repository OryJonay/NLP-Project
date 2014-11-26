import shutil,os,sys,TestingForACM
from TestingForACM import *




# input:
# 1- Data dir
# 2- num of k
def main():
    inDir = sys.argv[1]
    k = int(sys.argv[2]) 
    filesAmount = len(os.listdir(inDir))
    groupSize=int(filesAmount/k)
    i=0
    numOfChecks=1
    while i < k:
        j=1
        while j <= groupSize:
            filenum = (groupSize*i) + j
            shutil.move(inDir+'/'+str(filenum)+'.txt','Test')
            j+=1
        ACM = AutoCompModule('DB_'+str((i+1)))
        ACM.learn(inDir)
        print("iter num:"+str(i+1)+" checking every: "+str(numOfChecks))
        print(" simple test result:",round(simpleTest(ACM,'Test',numOfChecks)*100,2),end = ' ')
        print(" prob test result:",round(probTest(ACM,'Test',numOfChecks)*100,2))
        i+=1
        for file in os.listdir('Test'):
            shutil.move(file,inDir)

if __name__ == '__main__':
    main()
