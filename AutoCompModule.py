import pymongo, os, sys, re
from pymongo import Connection
from mongoHelper import Helper

weight3=50

class AutoCompModule:

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
    def learn(self,inputDir):
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
        self.helper.dictsToDbList()
        self.dict.insert(self.helper.list1)
        self.dictBy2.insert(self.helper.list2)
        self.dictBy3.insert(self.helper.list3)


    # Method that suggests the next word
    # For a given pprev and prev (definitions mentioned above) it finds the most likely word, one time
    # using only prev and the second using both pprev and prev
    # 
    # This method returns both NONE and NOT NONE values
    # None values are returned when there is no match to prev (or pprev and prev) in the dictionaries 
    # or when they are given as NONE
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
            return None , None
    
    def suggest2(self,pprev=None,prev=None,x=5):
        if prev is None:
            return None , None
        i=0
        lst=[]
        for a in self.dictBy2.find({"first": prev}).sort([('grade',-1),('second',1)]):
            if i<x:
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
                    if i<x:
                        lstBy3.append(a)
                        i+=1
                    else:
                        break
            if lstBy3 == []:
                return res1, None
            else:
                return res1,[[weight3*a["grade"],a["third"]] for a in lstBy3]

  