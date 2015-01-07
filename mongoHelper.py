import pymongo

class Helper():
    def __init__(self):
        self.dict1 = dict()
        self.dict2 = dict()
        self.dict3 = dict()
        self.infoDict = dict()
        self.list1 = []
        self.list2 = []
        self.list3 = []
        
    def insert(self,dict,args):
        if dict == self.dict1:
            if args in dict:
                dict[args] += 1
            else:
                dict[args] = 1
        else:
            if args in dict:
                dict[args] += 1
            else:
                dict[args] = 1 

    def dictsToDbList(self):
        if len(self.infoDict) == 0:
            self.infoDict = {key:[] for key in self.dict1}
        self.list1 = [{"word":key,"grade":self.dict1[key], "info":self.infoDict[key]} for key in self.dict1]
        self.list2 = [{"first":key[0],"second":key[1],"grade":self.dict2[key]} for key in self.dict2]
        self.list3 = [{"first":key[0],"second":key[1],"third":key[2],"grade":self.dict3[key]} for key in self.dict3]

    def insertMalletInfo(self,wordDict):
        for word in self.dict1:
            if word in wordDict:
                self.infoDict[word] = wordDict[word]
            else:
                self.infoDict[word] = None