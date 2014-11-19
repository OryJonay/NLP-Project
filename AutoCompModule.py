import pymongo, os, sys, re
from pymongo import Connection

class AutoCompModule:

    def __init__(self,DBName):
        self.dict = Connection()[DBName]['dict']
        self.dictBy2 = Connection()[DBName]['dictBy2']
        self.dictBy3 = Connection()[DBName]['dictBy3']
    
    def learnSingle(self,fileName):
        input = open(fileName, encoding='utf-8')
        for line in input:
            pprev = prev = None
            for word in line.split():
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    continue
            
                if self.dict.find_one({"word": word,"amount": { "$exists": True}}) != None:
                    self.dict.update({"word": word},{ "$inc": {"amount":1}})
                else:
                    self.dict.insert({"word": word, "amount":1})
            
                if prev!=None:
                    if self.dictBy2.find_one({"first": prev,"second": word,"grade": { "$exists": True}}) != None:
                        self.dictBy2.update({"first": prev,"second": word},{ "$inc": {"grade":1}})
                    else:
                        self.dictBy2.insert({"first": prev,"second": word,"grade":1})
                    if pprev!=None:
                        if self.dictBy3.find_one({"first": pprev,"second": prev,"third": word,"grade": { "$exists": True}}) != None:
                                  self.dictBy3.update({"first": pprev,"second": prev,"third": word},{ "$inc": {"grade":1}})
                        else:
                            self.dictBy3.insert({"first": pprev,"second": prev,"third": word,"grade":1})
                    pprev=prev
                prev = word
        input.close()

    def learn(self,inputDir):
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                self.learnSingle(inputDir + '/' + f)
                print ("SUCCESS LEARNING FOR \n",f)    
            print ("SUCCESS LEARNING FINISH\n")
        else:
            print ("ERROR!!")

    def suggest(self,pprev=None,prev=None):
        if prev is None:
            return None , None
        if pprev is None:
            a = self.dictBy2.find_one({"first": prev},sort=[("grade",-1),("second",1)])
            if a is not None:
                return a["second"] , None
            else:
                return None, None
        a = self.dictBy2.find_one({"first": prev},sort=[("grade",-1),("second",1)])
        b =  self.dictBy3.find_one({"first": pprev, "second": prev},sort=[("grade",-1),("third",1)])
        if b is not None:
            return a["second"] , b["third"]
        else:
            return a["second"] , None
    
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
                x1,x2 = self.simpleTestSingle(inputDir + '/' + f,num)
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
                    d = self.dictBy3.find_one({"first": pprev, "second": prev, "third": word}
                    if a is not None:
                        if c is not None:
                            biScore += (c["grade"])/(self.dictBy2.find_one({"first": prev, "second": a})["grade"])
                            biChecks += 1
                        else:
                            biScore = biScore
                    if b is not None:
                        if d is not None:
                            triScore += (d["grade"])/(self.dictBy3.find_one({"first": pprev, "second": prev, "third": b})["grade"])
                            triChecks += 1  
                        else:
                            triScore = triScore
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
                x1,x2 = self.probTestSingle(inputDir + '/' + f,num)
                sum1+=x1
                sum2+=x2
                numOfFiles+=1
            return sum1/numOfFiles, sum2/numOfFiles
        return "input Error"
