#! /usr/bin/python3.2
''' input: a directory of xml file of analyzed text
    output: a directory of all lexiconItems of analyses of positive score
'''
import sys
import os
import xml.etree.ElementTree as ET

def getLemma(inFile,outFile):
    root = ET.parse(inFile)
    for token in  root.getiterator('token'):
        for analysis in token.getiterator('analysis'):
            score =  analysis.get('score')
            if score is None or score == '0.0':
                continue
            for base in analysis.getiterator('base'):
                if base.get('lexiconItem') is None: #numbers and punctuation
                    surface = token.get('surface')
                    print(surface, end= ' ', file = outFile)
                    if surface in '.?!':
                        print( file = outFile)
                    
                else:
                    lex = base.get('lexiconItem')
                    print(lex, file=outFile, end = ' ')    
            break

if len(sys.argv) != 3:
    print('Usage: {a} inDir outDir or {a} inFile outFile'.format(a=sys.argv[0]))
    exit(1)
inDir = sys.argv[1]
if os.path.isdir(inDir):
    if not  os.path.isdir(sys.argv[2]):
        outDir = os.mkdir(sys.argv[2])
    for f in sorted(os.listdir(inDir)):
        g = f[:-3] + 'txt'
        with open(sys.argv[2] + '/' + g, 'w', encoding='utf-8') as outFile:
            print('inFile={}/{}\toutFile={}/{}'.format(sys.argv[1],f, sys.argv[2],g), file=sys.stderr)
            getLemma(inDir + '/' + f, outFile)
else:
    with open(sys.argv[2], 'w') as outFile:
        print('inFile={} outFile={}'.format(sys.argv[1], sys.argv[2]), file=sys.stderr)
        getLemma(inDir, outFile)
