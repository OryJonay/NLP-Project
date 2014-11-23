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
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = simpleTestSingle(ACM,inputDir + '/' + f,num)
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"
    
def probTestSingle(ACM, testFile, num):    
        test = open(testFile,'r',encoding='utf-8')
        biScore = triScore = 0.0
        biChecks = triChecks = 0
        i = num
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
                        biScore += (ACM.smooth(None,prev,word)/(ACM.smooth(None,prev,a)))
                        biChecks += 1
                    if b is not None:
                        triScore += (ACM.smooth(pprev,prev,word))/(ACM.smooth(pprev,prev,b))
                        triChecks += 1
                    i=num
                    pprev=prev
                    prev=word
        test.close()
        return biScore/biChecks, triScore/triChecks

def probTest(ACM,inputDir,num):
        sum1 = sum2 = 0
        numOfFiles = 0
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = probTestSingle(ACM,inputDir + '/' + f,num)
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
def main():
    #testing 1 2 3
    if len(sys.argv) is not 5:
        print ("Error - too few arguments. Arguments are: Database Name, Inpurt Directory, Test Type, Number of words to see\n")
    DBname = sys.argv[1]
    Indir = sys.argv[2]
    TestType = sys.argv[3]
    numOfChecks = int(sys.argv[4])

    ACM = AutoCompModule(DBname)
    
    if TestType == 's':
        print (simpleTest(ACM,Indir,numOfChecks))
    else:
        print (probTest(ACM,Indir,numOfChecks))


if __name__ == '__main__':
    print ("Working\n")
    main()