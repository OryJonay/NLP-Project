import pymongo, os, sys, re, subprocess , shutil
from pymongo import Connection
from AutoCompModule import AutoCompModule
import numpy as np

weight3 = 15

class ACM_LDA(AutoCompModule):
    def __init__(self, DBName):
        return super().__init__(DBName)
    def learn(self,inputDir,numTopics='15'):
        size = len(os.listdir(inputDir))
        i=1
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                self.learnSingle(inputDir + '/' + f)
                sys.stdout.flush()
                print(str(int((i*100)/size))+"%",end="\r") 
                i+=1   
            print ("SUCCESS LEARNING FINISH")
        else:
            print ("ERROR!!")
        DBName = self.name
        with open('trash.txt','w') as trashF:
            tv = subprocess.call(["mallet/bin/mallet","import-dir","--input",inputDir,"--output",DBName+".mallet","--keep-sequence","--token-regex","[\p{L}\p{P}]*\p{L}"],stdout=trashF,stderr=trashF)
            tv = subprocess.call(["mallet/bin/mallet","train-topics","--input",DBName+".mallet",'--inferencer-filename',DBName+'.inf',"--output-topic-keys",DBName+"-keys.txt","--topic-word-weights-file",DBName+"-twwf.txt","--word-topic-counts-file",DBName+"-wtcf.txt","--num-topics",numTopics,"--optimize-interval","20"],stdout=trashF,stderr=trashF)
        os.remove('trash.txt')
        self.addMalletInfoToDB(DBName+"-wtcf.txt", DBName+"-twwf.txt", DBName+"-keys.txt")
        self.helper.dictsToDbList()
        self.dict.insert(self.helper.list1)
        self.dictBy2.insert(self.helper.list2)
        self.dictBy3.insert(self.helper.list3)
        print ("SUCCESS MALLET FINISH")
        
    def addMalletInfoToDB(self, wtcfile, twwfile, keysfile):
        def malletGetWordTopicCounts(wtcfile):
            with open(wtcfile,'r', encoding='utf-8') as input:
                wordDict = {}
                for line in input:
                    tmp = line.split()
                    tmp.remove(tmp[0])
                    word = tmp[0]
                    tmp.remove(tmp[0])
                    wordData = []
                    currWordInDict = self.dict.find_one({"word":word})
                    if currWordInDict is not None:
                        currGrade = currWordInDict["grade"]
                    else:
                        currGrade = 1
                    for tc in tmp:
                        topicCount = tc.split(':')
                        wordData += [[int(topicCount[0]), int(topicCount[1])/currGrade, 0.0, False]]
                    wordDict[word] = wordData
                return wordDict

        def malletAddWeightsToWordDict(twwfile, wordDict):
            with open(twwfile, encoding='utf-8') as input:
                for line in input:
                    tww = line.split()
                    for wordData in wordDict[tww[1]]:
                        if wordData[0] == int(tww[0]):
                            wordData[2] = float(tww[2])
            
        def malletAddKeysToWordDict(keysfile, wordDict):
            with open(keysfile, encoding='utf-8') as input:
                for line in input:
                    tmp = line.split()
                    topic = int(tmp[0])
                    tmp.remove(tmp[0])
                    tmp.remove(tmp[0])
                    for word in tmp:
                        for wordData in wordDict[word]:
                            if wordData[0] == topic:
                                wordData[3] = True

        def malletGetWordsAndData(wtcfile, twwfile, keysfile):
            wordDict = malletGetWordTopicCounts(wtcfile)
            malletAddWeightsToWordDict(twwfile, wordDict)
            malletAddKeysToWordDict(keysfile, wordDict)
            return wordDict

        wordDict = malletGetWordsAndData(wtcfile, twwfile, keysfile)
        h = self.helper
        h.insertMalletInfo(wordDict)
        #for word in wordDict:
           # if self.dict.find_one({"word": word,"grade": { "$exists": True}}) != None:
            #    self.dict.update({"word": word},{"$set":{"info": wordDict[word]}})

    def suggestTopTopic(self,pprev=None,prev=None,bestTopic=[],x=5):
        if prev is None:
            return None,None
        i=0
        lst=[]
        for a in self.dictBy2.find({"first": prev}).sort([('grade',-1),('second',1)]):
            if i<x:
                c=self.dict.find_one({"word":a["second"]})
                if c["info"] is not None:
                       B=c["info"]
                       btCount = [0,0,0]
                       for b in B:
                           if b[0] in bestTopic:
                               btCount[0]+=1
                               btCount[1]+=b[1]
                               if b[3] == True:
                                    btCount[2]+=1
                       if btCount[0] > 0:
                           lst += [btCount+[a["grade"], a["second"]]]
                           i+=1        
            else:
                break
        if lst == []:
            lst = None
        else:
            lst.sort(reverse=True)
        if pprev is None:
            return lst,None
        else:
            i=0
            lst2=[]
            for a in self.dictBy3.find({"first": pprev, "second": prev}).sort([('grade',-1),('third', 1)]):
                if i<x:
                    c=self.dict.find_one({"word":a["third"]})
                    if c["info"] is not None:
                       B=c["info"]
                       btCount = [0,0,0]
                       for b in B:
                           if b[0] in bestTopic:
                               btCount[0]+=1
                               btCount[1]+=b[1]
                               if b[3] == True:
                                    btCount[2]+=1
                       if btCount[0] > 0:
                           lst2 += [btCount+[weight3*a["grade"], a["third"]]]
                           i+=1
                else:
                    break
            if lst2 == []:
                return lst,None
            lst2.sort(reverse=True)
            return lst,lst2

    def suggest(self,pprev=None,prev=None,buff=[],x=5):
        if len(buff) < 10:
            return None
        a,b = self.suggest2(pprev,prev,x)
        if a==None and b==None:
            return None
        c = []
        if b==None:
            c = a
        else:
            c = a+b
        c = [k for k in set([i[1] for i in c])]
        sBuff = ' '.join(buff)
        os.mkdir("tmp")
        with open("tmp/temp0.txt",'w',encoding = 'utf=8') as base:
            base.write(sBuff)
        i=1
        for j in c:
            s= sBuff+' '+j
            with open("tmp/temp"+str(i)+".txt",'w',encoding='utf-8') as temp_file:
                temp_file.write(s)
            i += 1
        with open('tmp/dmpFile.txt','w') as dmp:
            tv = subprocess.call(["mallet/bin/mallet","import-dir","--input","tmp","--output","tmp/tmp.mallet","--keep-sequence","--token-regex","[\p{L}\p{P}]*\p{L}"],stdout=dmp,stderr=dmp)
            tv = subprocess.call(["mallet/bin/mallet","infer-topics","--inferencer",str(self.name)+".inf","--input","tmp/tmp.mallet","--output-doc-topics","tmp/tmp-doc.txt"],stdout=dmp,stderr=dmp)
        d = {}
        with open("tmp/tmp-doc.txt",'r',encoding='utf-8') as results:
            for line in results:
                if len(line.split()) == 5:
                    continue
                raw_data = line.split()[2:]
                td = [(raw_data[i],raw_data[i+1]) for i in range(0,len(raw_data),2)]
                td.sort()
                d[int(line.split()[0])] = np.array([float(tup[1]) for tup in td])  
        for item in range(1,len(d)):
            d[item] = sum(abs(d[0] - d[item]))

        r = [(d[i+1],c[i]) for i in range(len(c))]
        r.sort()       
        shutil.rmtree("tmp") 
        return [w[1] for w in r]
            
    
def main():
    ACM = ACM_LDA('DB_Mall')
    ACM.addMalletInfoToDB('MalletData\Data-wtcf.txt', 'MalletData\Data-twwf.txt', 'MalletData\Data-keys.txt')

if __name__=='__main__':
    main()
