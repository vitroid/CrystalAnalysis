#!/usr/bin/env python
# detect tetrahedra
#
#read @NGPH

import re
import sys
import string

spaces=re.compile(" +")

def spacesplit(line):
    line = string.rstrip(line," \t\r\n")
    columns=spaces.split(line)
    while columns[0] == "":
        columns.pop(0)
    return columns

def readNGPH( filehandle ):
    ngph = re.compile("^@NGPH")
    #graph = dict()
    while True:
        #Seek @NGPH tag
        line = filehandle.readline()
        #if EOF
        if line == "":
            return None
        #if line begins with "@NGPH"
        result = ngph.search(line)
        if result:
            #first line is number of nodes
            columns = map(int,spacesplit(filehandle.readline()))
            numnodes = columns[0]
            neighbors = []
            for i in range(numnodes):
                neighbors.append([])
            while True:
                #node pairs (=bond) follows
                columns = map(int,spacesplit(filehandle.readline()))
                if columns[0] < 0:
                    #return graph
                    return neighbors
                #graph[(columns[0],columns[1])] =  1
                #graph[(columns[1],columns[0])] = -1
                neighbors[columns[0]].append(columns[1])
                neighbors[columns[1]].append(columns[0])

while True:
    tetrahedra = []
    neighbors = readNGPH(sys.stdin)
    if neighbors == None:
        break
    print "@FRAG"
    print 4,len(neighbors)
    for i in range(len(neighbors)):
        js = neighbors[i]
        for j in js:
            if i < j:
                ks = neighbors[j]
                for k in ks:
                    if j < k and k in neighbors[i]:
                        ls = neighbors[k]
                        for l in ls:
                            if k < l and l in neighbors[i] and l in neighbors[j]:
                                print i,j,k,l
    print -1,-1,-1,-1

                            

            
