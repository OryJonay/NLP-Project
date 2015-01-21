from ACM import ACM
import os,re,sys
from time import clock

def timed(f):
    '''decorator for printing the timing of functions
    usage: 
    @timed
    def some_funcion(args...):'''
    
    def wrap(*x, **d):
        start = clock()
        res = f(*x, **d)
        print(f.__name__, ':', clock() - start)
        return res
    return wrap

def weight_expr(ACM,test_dir):
    @timed
    def TestForFile(ACM,testFile,weight,checkSpace=1,listSize=10,listTstSize=5):
        with open(testFile,'r',encoding='utf-8') as test:
            numOfChecks = 0
            succ = 0
            i = checkSpace
            for line in test:
                pprev = prev = None
                for word in line.split():
                    if re.match("[.,\"\(\);']",word):
                        pprev = prev = word = None
                        i = checkSpace
                        continue
                    if i!= 0:
                        i-=1
                        pprev = prev
                        prev = word
                    else:
                        a,b = ACM.getBestLists(pprev,prev,listSize,weight)
                        if a is None:
                            pprev = prev
                            prev = word
                            continue
                        simp_res = ACM.setListByNgram(a,b)
                        succ = succ + 1 if word in simp_res[:listTstSize] else succ
                        numOfChecks += 1
                        pprev=prev
                        prev=word
            numOfChecks = numOfChecks if numOfChecks > 0 else 1
            return succ / numOfChecks            
    size = len(os.listdir(test_dir))
    i=1
    sums = {i:0 for i in range(10,101,10)}
    if os.path.isdir(test_dir):
        for weight in sums:
            for f in sorted(os.listdir(test_dir)):
                res = TestForFile(ACM,test_dir + '/' + f, weight)
                sys.stdout.flush()
                print(str(int((i*10)/size))+"%",end="\r") 
                i+=1
                sums[weight] += res
            
        return {i:sums[i]/size for i in sorted(sums)}
    return "input Error"

def buff_size_expr(ACM,test_dir):
    def TestForFile(ACM,testFile,weight=50,checkSpace=1,listSize=10,listTstSize=5,buffSize = 15):
        with open(testFile,'r',encoding='utf-8') as test:
            numOfChecks = 0
            succ = 0
            buff = []
            i = checkSpace
            for line in test:
                pprev = prev = None
                for word in line.split():
                    buff += word
                    if len(buff) > buffSize:
                        buff.pop(0)
                    if re.match("[.,\"\(\);']",word):
                        pprev = prev = word = None
                        i = checkSpace
                        continue
                    if i!= 0:
                        i-=1
                        pprev = prev
                        prev = word
                    else:
                        a,b = ACM.getBestLists(pprev,prev,listSize,weight)
                        if a is None:
                            pprev = prev
                            prev = word
                            continue
                        top_res = ACM.setListByTopic(a,b,buff)
                        succ = succ + 1 if word in top_res[:listTstSize] else succ
                        numOfChecks += 1
                        pprev=prev
                        prev=word
            numOfChecks = numOfChecks if numOfChecks > 0 else 1
            return succ / numOfChecks            
    size = len(os.listdir(test_dir))
    i=1
    sums = {i:0 for i in range(15,121,15)}
    if os.path.isdir(test_dir):
        for buff_size in sums:
            for f in sorted(os.listdir(test_dir)):
                res = TestForFile(ACM,test_dir + '/' + f, buffSize = buff_size)
                sys.stdout.flush()
                print(str(int((i*100)/(size*8)))+"%",end="\r") 
                i+=1
                sums[buff_size] += res
            
        return {i:sums[i]/size for i in sorted(sums)}
    return "input Error"
    