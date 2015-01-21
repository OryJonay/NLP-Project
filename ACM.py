from mongoHelper import Helper
import pymongo, os, sys, re, subprocess , shutil
from pymongo import Connection
from AutoCompModule import AutoCompModule
import numpy as np

class ACM:

    # Auto completion module
    # Using the MongoDB server
    # Holds three dictionaries :
    #   dict - holds the amount of x's appearances in the learned text
    #   dictBy2 - holds the amount of (x,y) appearances in the learned text
    #   dictBy2 - holds the amount of (x,y,z) appearances in the learned text
    def __init__(self,DBName):
        connect = 'mongodb://project:project1234@yeda.cs.technion.ac.il/'
        self.conn = Connection(connect+DBName)
        self.dict = self.conn[DBName]['dict']
        self.dictBy2 = self.conn[DBName]['dictBy2']
        self.dictBy3 = self.conn[DBName]['dictBy3']
        self.name = DBName
        self.helper = Helper()
    # Dropping the database to delete all data
    
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
    
    def dropDicts(self,DBName):
        self.conn.drop_database(DBName)
    
    # Method to learn from a single file
    # For each file the method detects all the information mentioned above
    # Definitions :
    #   pprev,prev,word are the three last seen words (where word is the current word) 
    
    def learnSingle(self,fileName):
        h = self.helper
        with open(fileName,encoding='utf-8') as input:
            for line in input:
                pprev = prev = None
                for word in line.split():
                    if re.match("[.,\"\(\);:%?!-@#$^&*\{\[\}\]\']",word):
                        pprev = prev = word = None
                        continue
                    h.insert(h.dict1,word)
                    if prev!=None:
                        h.insert(h.dict2,(prev,word))
                        if pprev!=None:
                            h.insert(h.dict3,(pprev,prev,word))
                        pprev=prev
                    prev = word

    # Method to learn from multiple files
    # Uses learnSingle Method
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
    
    def getBestLists(self,pprev=None,prev=None,listSize=5,weight3=50):
        if prev is None:
            return None , None
        i=0
        lst=[]
        for a in self.dictBy2.find({"first": prev}).sort([('grade',-1),('second',1)]):
            if i<listSize:
                lst.append(a)
                i+=1
            else:
                break
        if lst == []:
            return None, None
        else:
            res1 = [[a["grade"],a["second"]] for a in lst]       
        if pprev is None:
            return res1, None
        else:
            i=0
            lstBy3=[]
            for a in self.dictBy3.find({"first": pprev,"second":prev}).sort([('grade',-1),('second',1)]):
                    if i<listSize:
                        lstBy3.append(a)
                        i+=1
                    else:
                        break
            if lstBy3 == []:
                return res1, None
            else:
                return res1,[[weight3*a["grade"],a["third"]] for a in lstBy3]

    def setListByNgram(self,lst1,lst2):
        if lst1 is None:
            return None
        if lst2 is None:
            return [lst1[i][1] for i in range(len(lst1))]
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
        return [resLst[i][1] for i in range(len(resLst))]
  
    def setListByTopic(self,lst1,lst2,buff):
        if lst1==None and lst2==None:
            return None
        resLst = []
        if lst2==None:
            resLst = lst1
        else:
            resLst = lst1+lst2
        resLst = [k for k in set([i[1] for i in resLst])]
        sBuff = ' '.join(buff)
        os.mkdir("tmp")
        with open("tmp/temp0.txt",'w',encoding = 'utf=8') as base:
            base.write(sBuff)
        i=1
        for j in resLst:
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

        r = [(d[i+1],resLst[i]) for i in range(len(resLst))]
        r.sort()       
        shutil.rmtree("tmp") 
        return [w[1] for w in r]

        