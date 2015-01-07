import AutoCompModule
from AutoCompModule import AutoCompModule
import pymongo, os, sys, re
import ACM_LDA
from ACM_LDA import ACM_LDA

# Testing for the AutoCompModule


def simpleTestSingle(ACM, testFile, num):
        
    with open(testFile,'r',encoding='utf-8') as test:
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
        numOfChecks1 = numOfChecks1 if numOfChecks1 > 0 else 1
        numOfChecks2 = numOfChecks2 if numOfChecks2 > 0 else 1 
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

def impSimTestSingle(ACM, testFile, num, numOfElemList=5):
        
    with open(testFile,'r',encoding='utf-8') as test:
        numOfChecks = succ = 0
        i = num
        def alphaFunc(lst1,lst2,numOfElemList):
            if lst1 is None:
                return None
            if lst2 is None:
                lst1.sort()
                return [lst1[i][1] for i in range(len(lst1)) if i <= (numOfElemList-1)]
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
            resLst.sort(reverse=True)
            return [resLst[i][1] for i in range(len(resLst)) if i <= (numOfElemList-1)]

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
                    lstBy2,lstBy3 = ACM.suggest2(pprev,prev,2*numOfElemList)
                    a = alphaFunc(lstBy2,lstBy3,numOfElemList)
                    if a is not None:
                        if word in a:
                            succ+=1
                        numOfChecks+=1
                    i=num
                    pprev=prev
                    prev=word
        numOfChecks = numOfChecks if numOfChecks > 0 else 1
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
        
    with open(testFile,'r',encoding='utf-8') as test:
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
        
        biChecks = biChecks if biChecks >0 else 1
        triChecks = triChecks if triChecks >0 else 1
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

def simTopicTest(ACM,testFile,num,numTopics,numOfElemList1,numOfElemList2,numLastTopics,numOfBestTopics):
    def topicFunc(lst1,lst2,numOfElemList):
            if lst1 is None:
                if lst2 is None:
                    return None
                else:
                    return [lst2[i][4] for i in range(len(lst2)) if i <= (numOfElemList-1)]
            if lst2 is None:
                return [lst1[i][4] for i in range(len(lst1)) if i <= (numOfElemList-1)]
            resLst = []
            for a in lst1:
                for b in lst2:
                    if a[4]==b[4]:
                        a[3]+=b[3]
                        break
                resLst.append(a)
            for b in lst2:
                flag = False
                for a in resLst:
                    if a[4] == b[4]:
                        flag = True
                        break
                if not flag:
                    resLst.append(b)
            resLst.sort(reverse=True)
            return [resLst[i][4] for i in range(len(resLst)) if i <= (numOfElemList-1)]

    def fBestTopic(vtopics,numOfBestTopics):
        vtlist = []
        for t in vtopics:
            tmp = vtopics[t] + [t]
            vtlist += [tmp]
        vtlist.sort(reverse=True)
        return [vtlist[i][3] for i in range(numOfBestTopics)]

    def fBestTopic2(lastTopics,numOfBestTopics):
        tmpV = {i:[0,0,0] for i in range(numTopics)}
        for winfo in lastTopics:
            for t in winfo:
                tmpV[t[0]][0] += 1
                tmpV[t[0]][1] += t[1]
                if t[3] == True:
                    tmpV[t[0]][2] += 1
        return fBestTopic(tmpV,numOfBestTopics)

    with open(testFile,'r',encoding='utf-8') as test:
        vtopics = {i:[0,0,0] for i in range(numTopics)}
        lastTopics = []
        numInLastTopics = 0
        i = num
        numOfChecks = succ = numOfChecks2 = succ2 = 0
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
                        lstBy2,lstBy3 = ACM.suggestTopTopic(pprev,prev,fBestTopic(vtopics,numOfBestTopics),numOfElemList2)
                        a = topicFunc(lstBy2,lstBy3,numOfElemList1)
                        if a is not None:
                            if word in a:
                                succ+=1
                            numOfChecks+=1
                        lstBy2,lstBy3 = ACM.suggestTopTopic(pprev,prev,fBestTopic2(lastTopics,numOfBestTopics),numOfElemList2)
                        a = topicFunc(lstBy2,lstBy3,numOfElemList1)
                        if a is not None:
                            if word in a:
                                succ2+=1
                            numOfChecks2+=1
                        i=num
                        pprev=prev
                        prev=word
                    wordInDict = ACM.dict.find_one({"word":prev})
                    if wordInDict is not None:
                        wordInfo=wordInDict["info"]
                        if wordInfo is not None:
                            for a in wordInfo:
                                vtopics[a[0]][0]+=1
                                vtopics[a[0]][1]+=a[1]
                                if a[3] is True:
                                    vtopics[a[0]][2]+=1
                            if len(lastTopics) < numLastTopics:
                                lastTopics +=[wordInfo]
                            else:
                                lastTopics.pop(0)
                                lastTopics+=[wordInfo]
    return succ/numOfChecks, succ2/numOfChecks2

 

def topicTest(ACM,inputDir,num,numTopics,numOfElemList1,numOfElemList2,numLastTopics,numOfBestTopics):
        sum1 = sum2 = 0
        numOfFiles = 0
        size = len(os.listdir(inputDir))
        i=1
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                x1,x2 = simTopicTest(ACM,inputDir + '/' + f,num,numTopics,numOfElemList1,numOfElemList2,numLastTopics,numOfBestTopics)
                sys.stdout.flush()
                print(str(int((i*100)/size))+"%",end="\r") 
                i+=1  
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"

def diffTopicTest(ACM,testFile,num,numElmCut,numElmX,maxBuff=float('inf')):
    with open(testFile,'r',encoding='utf-8') as test:
        numOfChecks1 = numOfChecks2 = succ1 = succ2 = 0
        i = num
        buff = []
        for line in test:
            pprev = prev = None
            for word in line.split():
                buff += [word]
                if len(buff) > maxBuff:
                    buff.pop(0)
                    
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    i = num
                    continue
                if i!= 0:
                    i-=1
                    pprev = prev
                    prev = word
                else:
                    a = ACM.suggest(pprev,prev,buff,numElmX)
                    if a is not None:
                        if word in a[:numElmCut]:
                            succ1+=1
                        numOfChecks1+=1
                    i=num
                    pprev=prev
                    prev=word
        numOfChecks1 = numOfChecks1 if numOfChecks1 > 0 else 1 
        return succ1/numOfChecks1

def diffTest(ACM,inputDir,num,numElmCut,numElmX,maxBuff=float('inf')):
    print ('Start testing')
    sum1 =  0
    size = len(os.listdir(inputDir))
    i=1
    if os.path.isdir(inputDir):
        for f in sorted(os.listdir(inputDir)):
            x1 = diffTopicTest(ACM,inputDir + '/' + f,num,numElmCut,numElmX,maxBuff)
            sys.stdout.flush()
            print(str(int((i*100)/size))+"%",end="\r") 
            i+=1
            sum1+=x1
        return sum1/size
    return "input Error"

# Input for the testing::
#   1 - the database name we want to check
#   2 - the directory we want to test
#   3 - the test type
#   4 - num of checks

def main():
    #testing 1 2 3
    if len(sys.argv) > 6:
        print ("Error - too few arguments. Arguments are: Database Name, Inpurt Directory, Test Type, Number of words to see\n")
    DBname = sys.argv[1]
    Indir = sys.argv[2]
    action = sys.argv[3]
    if action != 'learn':
        numOfChecks = int(sys.argv[4])

    ACM = ACM_LDA(DBname)
    
    
    if action == 'learn':
        ACM.learn(Indir)
    if action == 'simple':
        (x,y) = simpleTest(ACM,Indir,numOfChecks)
        print (round(x*100,2),round(y*100,2))
    if action == 'prob':
        (x,y) = probTest(ACM,Indir,numOfChecks)
        print (round(x*100,2),round(y*100,2))
    if action == 'isimple':
        #   5 - num of elements to choose from table
        ACM.dropDicts(DBname)
        ACM.learn('corpus')
        numElem = int(sys.argv[5])
        x = impSimTest(ACM,Indir,numOfChecks,numElem)
        print (round(x*100,2))
    if action == 'sTopic':
        ACM = ACM_LDA(DBname)
        (x,y) = topicTest(ACM,Indir,numOfChecks,15,5,7,15,3)
        print (round(x*100,2),round(y*100,2))
    if action == 'best100':
        i=0
        with open('ilaiOut.txt','w') as outfile:
            for a in ACM.dict.find().sort([("grade",-1)]):
                if i < 100:
                    outfile.write(str(a)+'\n')
                    i+=1
                else:
                    break
    if action == 'diff':
        ACM.dropDicts(DBname)
        ACM.learn(Indir)
        print ("done learning. starting test.")
        print (diffTest(ACM, Indir+'test', numOfChecks, 5, 5))



if __name__ == '__main__':
    main()