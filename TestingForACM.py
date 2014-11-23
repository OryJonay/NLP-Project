import AutoCompModule
from AutoCompModule import AutoCompModule
import pymongo, os, sys, re

# Testing for the AutoCompModule


def simpleTestSingle(self, testFile, num):
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
                    a,b = self.suggest(pprev,prev)
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

def simpleTest(self,inputDir,num):
        sum1 = sum2 = 0
        numOfFiles = 0
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = simpleTestSingle(self,inputDir + '/' + f,num)
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"
    
def probTestSingle(self, testFile, num):    
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
                    a,b = self.suggest(pprev,prev)
                    c = self.dictBy2.find_one({"first": prev, "second": word})
                    d = self.dictBy3.find_one({"first": pprev, "second": prev, "third": word})
                    if a is not None:
                        if c is not None:
                            biScore += (c["grade"])/(self.dictBy2.find_one({"first": prev, "second": a})["grade"])
                        else:
                            biScore = biScore
                        biChecks += 1
                    if b is not None:
                        if d is not None:
                            triScore += (d["grade"])/(self.dictBy3.find_one({"first": pprev, "second": prev, "third": b})["grade"])
                        else:
                            triScore = triScore
                        triChecks += 1
                    i=num
                    pprev=prev
                    prev=word
        test.close()
        return biScore/biChecks, triScore/triChecks

def probTest(self,inputDir,num):
        sum1 = sum2 = 0
        numOfFiles = 0
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = probTestSingle(self,inputDir + '/' + f,num)
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
    if len(sys.argv) is not 5:
        print ("Error - too few arguments. Arguments are: Database Name, Inpurt Directory, Test Type, Number of words to see\n")
    DBname = sys.argv[1]
    Indir = sys.argv[2]
    TestType = sys.argv[3]
    numOfChecks = int(sys.argv[4])

    DB = AutoCompModule(DBname)
    
    if TestType == 's':
        print (simpleTest(DB,Indir,numOfChecks))
    else:
        print (probTest(DB,Indir,numOfChecks))


if __name__ == '__main__':
    print ("Working\n")
    main()