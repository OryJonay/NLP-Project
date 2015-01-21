import pymongo, os, sys, re
import ACM
from ACM import ACM
import numpy as np
from time import clock

def check_success(word,lst1,lst2,lst3,succ):
    succ["ngram"] = succ["ngram"] + 1 if word in lst1 else succ["ngram"]
    succ["topic"] = succ["topic"] + 1 if word in lst2 else succ["topic"]
    succ["snipped_topic"] = succ["snipped_topic"] + 1 if word in lst3 else succ["snipped_topic"]

def TestForFile(ACM,testFile,checkSpace,listSize,listTstSize,buffSize):
    with open(testFile,'r',encoding='utf-8') as test:
        numOfChecks = 0
        succ = {"ngram":0,"topic":0,"snipped_topic":0}
        i = checkSpace
        buff = []
        for line in test:
            pprev = prev = None
            for word in line.split():
                buff += [word]
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    i = checkSpace
                    continue
                if i!= 0:
                    i-=1
                    pprev = prev
                    prev = word
                else:
                    start = clock()
                    a,b = ACM.getBestLists(pprev,prev,listSize)
                    print ('Extracting from DB',clock()-start)
                    if a is None:
                        pprev = prev
                        prev = word
                        continue
                    snipped_buff = buff[-1:buffSize-1:-1]
                    snipped_buff.reverse()
                    if buffSize > len(buff):
                        snipped_buff = buff
                    start = clock()
                    simp_res = ACM.setListByNgram(a,b)
                    print ('Simple test',clock()-start)
                    start = clock()
                    top_res = ACM.setListByTopic(a,b,buff)
                    print ('Topic test',clock()-start)
                    start = clock()
                    top_sbuff_res = ACM.setListByTopic(a,b,snipped_buff)
                    print ('Snipped Topic test',clock()-start)
                    check_success(word, simp_res[:listTstSize], top_res[:listTstSize], top_sbuff_res[:listTstSize], succ)
                    numOfChecks += 1
                    pprev=prev
                    prev=word
        numOfChecks = numOfChecks if numOfChecks > 0 else 1
        
        return {i:succ[i]/numOfChecks for i in succ}


def Test(ACM,inputDir,checkSpace=1,numElmCut=10,numElmX=5,maxBuff=10):
    print ('Start testing')
    sums =  {"ngram":0,"topic":0,"snipped_topic":0}
    size = len(os.listdir(inputDir))
    i=1
    if os.path.isdir(inputDir):
        for f in sorted(os.listdir(inputDir)):
            res = TestForFile(ACM,inputDir + '/' + f,checkSpace,numElmCut,numElmX,maxBuff)
            sys.stdout.flush()
            print(str(int((i*100)/size))+"%",end="\r") 
            i+=1
            sums = {i:sums[i]+res[i] for i in sums}
        
        return {i:sums[i]/size for i in sums}
    return "input Error"

if __name__ == '__main__':
    from sys import argv
    acm = ACM('db1')
    acm.dropDicts('db1')
    acm.learn(argv[1])
    print (Test(acm,argv[2]))