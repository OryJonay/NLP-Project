import pymongo, os, sys, re
from pymongo import Connection

class AutoCompModule:

    # Auto completion module
    # Using the MongoDB server
    # Holds three dictionaries :
    #   dict - holds the amount of x's appearances in the learned text
    #   dictBy2 - holds the amount of (x,y) appearances in the learned text
    #   dictBy2 - holds the amount of (x,y,z) appearances in the learned text
    def __init__(self,DBName):
        self.dict = Connection()[DBName]['dict']
        self.dictBy2 = Connection()[DBName]['dictBy2']
        self.dictBy3 = Connection()[DBName]['dictBy3']
    
    
    # Method to learn from a single file
    # For each file the method detects all the information mentioned above
    # Definitions :
    #   pprev,prev,word are the three last seen words (where word is the current word) 
    def learnSingle(self,fileName):
        input = open(fileName, encoding='utf-8')
        for line in input:
            pprev = prev = None
            for word in line.split():
                if re.match("[.,\"\(\);']",word):
                    pprev = prev = word = None
                    continue
            
                if self.dict.find_one({"word": word,"grade": { "$exists": True}}) != None:
                    self.dict.update({"word": word},{ "$inc": {"grade":1}})
                else:
                    self.dict.insert({"word": word, "grade":1})
            
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


    # Method to learn from multiple files
    # Uses learnSingle Method
    def learn(self,inputDir):
        if os.path.isdir(inputDir):
            for f in sorted(os.listdir(inputDir)):
                self.learnSingle(inputDir + '/' + f)
                print ("SUCCESS LEARNING FOR \n",f)    
            print ("SUCCESS LEARNING FINISH\n")
        else:
            print ("ERROR!!")


    # Method that suggests the next word
    # For a given pprev and prev (definitions mentioned above) it finds the most likely word, one time
    # using only prev and the second using both pprev and prev
    # 
    # This method returns both NONE and NOT NONE values
    # None values are returned when there is no match to prev (or pprev and prev) in the dictionaries 
    # or when they are gives as NONE
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
    

