import pymongo, os, sys
from pymongo import MongoClient

def main():
    x=7
    y=8
    input = open(sys.argv[1], encoding='utf-8')
    words = MongoClient().db.words
    words2 = MongoClient().db.words2
    output = open("output.txt","w", encoding='utf-8')

    for line in input:
        prev=None
        pprev=None
        for word in line.split():
            if prev!=None:
                if words.find_one({"first": prev,"second": word,"grade": { "$exists": True}}) != None:
                              words.update({"first": prev,"second": word},{ "$inc": {"grade":1}})
                else:
                    words.insert({"first": prev,"second": word,"grade":1})
                if pprev!=None:
                    if words2.find_one({"first": pprev,"second": prev,"third": word,"grade": { "$exists": True}}) != None:
                              words2.update({"first": pprev,"second": prev,"third": word},{ "$inc": {"grade":1}})
                    else:
                        words2.insert({"first": pprev,"second": prev,"third": word,"grade":1})
                pprev=prev
            prev = word
    for i in words.find(): output.write("first: "+str(i["first"])+"  second: "+str(i["second"])+"  grade: "+str(i["grade"])+"\n")
    for i in words2.find(): output.write("first: "+str(i["first"])+"  second: "+str(i["second"])+"  third: "+str(i["third"])+"  grade: "+str(i["grade"])+"\n")



if __name__ == '__main__':
    print ("Working\n")
    main()
