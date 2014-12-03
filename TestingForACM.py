import AutoCompModule
from AutoCompModule import AutoCompModule
import pymongo, os, sys, re

# Testing for the AutoCompModule


def simpleTestSingle(ACM, testFile, num):
        test = open(testFile,'r',encoding='utf-8')
        numOfChecks1 = numOfChecks2 = succ1 = succ2 = 0
        i = num
        for line in test:
            pprev = prev = None
            for word in line.split():
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    i = num
                    continue
                if i!= 0:
                    i-=1
                    pprev = prev
                    prev = word
                else:
                    a,b = ACM.suggest(pprev,prev)
                    if a is not None:
                        if a is word:
                            succ1+=1
                        numOfChecks1+=1
                    if b is not None:
                        if b is word:
                            succ2+=1
                        numOfChecks2+=1
                    i=num
                    pprev=prev
                    prev=word
        test.close()
        return succ1/numOfChecks1, succ2/numOfChecks2

def simpleTest(ACM,inputDir,num):
        sum1 = sum2 = 0
        numOfFiles = 0
        size = len(os.listdir(inputDir))
        i=1
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = simpleTestSingle(ACM,inputDir + '/' + f,num)
                sys.stdout.flush()
                print(str(int((i*100)/size))+"%",end="\r") 
                i+=1  
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"

def impSimTestSingle(ACM, testFile, num, numOfElemList):
        test = open(testFile,'r',encoding='utf-8')
        numOfChecks = succ = 0
        i = num
        def alphaFunc(lst1,lst2):
            if lst1 is None:
                return None
            if lst2 is None:
                return max(lst1)[1]
            resLst = []
            for a in lst1:
                for b in lst2:
                    if a[1]==b[1]:
                        a[0]+=b[0]
                        break
                resLst.append(a)
            for b in lst2:
                flag = False
                for a in resLst:
                    if a[1] == b[1]:
                        flag = True
                        break
                if not flag:
                    resLst.append(b)
            return max(resLst)[1]

        for line in test:
            pprev = prev = None
            for word in line.split():
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    i = num
                    continue
                if i!= 0:
                    i-=1
                    pprev = prev
                    prev = word
                else:
                    lstBy2,lstBy3 = ACM.suggest2(pprev,prev,numOfElemList)
                    a = alphaFunc(lstBy2,lstBy3)
                    if a is not None:
                        if a is word:
                            succ+=1
                        numOfChecks+=1
                    i=num
                    pprev=prev
                    prev=word
        test.close()
        return succ/numOfChecks

def impSimTest(ACM,inputDir,num,x):
        sum = 0
        numOfFiles = 0
        size = len(os.listdir(inputDir))
        i=1
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                res = impSimTestSingle(ACM,inputDir + '/' + f,num,x)
                sys.stdout.flush()
                print(str(int((i*100)/size))+"%",end="\r") 
                i+=1  
                sum+=res
                numOfFiles+=1
            return sum/numOfFiles
        return "input Error"
    
def probTestSingle(ACM, testFile, num):    
        test = open(testFile,'r',encoding='utf-8')
        biScore = triScore = 0.0
        biChecks = triChecks = 0
        i = num
        def smooth(ACM,pprev,prev,word):
            if pprev is None:
                res = ACM.dictBy2.find_one({"first":prev,"second":word})
                if res is None:
                        res = 1
                else:
                   res = ACM.dictBy2.find_one({"first":prev,"second":word})["grade"]+1
            else:
                res = ACM.dictBy3.find_one({"first":pprev,"second":prev,"third":word})
                if res is None:
                    res = 1
                else:
                    res = ACM.dictBy3.find_one({"first":pprev,"second":prev,"third":word})["grade"]+1
            return res

        for line in test:
            pprev = prev = None
            for word in line.split():
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    i = num
                    continue
                if i != 0:
                    i -= 1
                    pprev = prev
                    prev = word
                else:
                    a,b = ACM.suggest(pprev,prev)
                    if a is not None:
                        biScore += (smooth(ACM,None,prev,word)/(smooth(ACM,None,prev,a)))
                        biChecks += 1
                    if b is not None:
                        triScore += (smooth(ACM,pprev,prev,word))/(smooth(ACM,pprev,prev,b))
                        triChecks += 1
                    i=num
                    pprev=prev
                    prev=word
        test.close()
        return biScore/biChecks, triScore/triChecks

def probTest(ACM,inputDir,num):
        sum1 = sum2 = 0
        numOfFiles = 0
        size = len(os.listdir(inputDir))
        i=1
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = probTestSingle(ACM,inputDir + '/' + f,num)
                sys.stdout.flush()
                print(str(int((i*100)/size))+"%",end="\r") 
                i+=1   
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"


# Input for the testing::
#   1 - the database name we want to check
#   2 - the directory we want to test
#   3 - the test type
#   4 - num of checks
#   5 - num of elements to choose from table
def main():
    #testing 1 2 3
    if len(sys.argv) > 6:
        print ("Error - too few arguments. Arguments are: Database Name, Inpurt Directory, Test Type, Number of words to see\n")
    DBname = sys.argv[1]
    Indir = sys.argv[2]
    action = sys.argv[3]
    if action != 'l':
        numOfChecks = int(sys.argv[4])

    ACM = AutoCompModule(DBname)
    
    if action == 'l':
        ACM.learn(Indir)
    if action == 's':
        (x,y) = simpleTest(ACM,Indir,numOfChecks)
        print (round(x*100,2),round(y*100,2))
    if action == 'p':
        (x,y) = probTest(ACM,Indir,numOfChecks)
        print (round(x*100,2),round(y*100,2))
    if action == 'i':
        numElem = int(sys.argv[5])
        x = impSimTest(ACM,Indir,numOfChecks,numElem)
        print (round(x*100,2))

if __name__ == '__main__':
    main()