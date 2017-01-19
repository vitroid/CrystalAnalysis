#!/usr/bin/env python
# coding: utf-8

#read water configurations in NX4A format,
#calculate the pairwise products of local order parameter for ice 7,
#and output them with pair distances.

#2012-10-19 tested with ice VII crystal structure.

import numpy
import numpy.linalg
import math
import sys
import itertools
import random

import pairlist

############################################################################## Quaternion
def quat2rotmat(q):
    a,b,c,d = q
    sp11=(a*a+b*b-(c*c+d*d))
    sp12=-2.0*(a*d+b*c)
    sp13=2.0*(b*d-a*c)
    sp21=2.0*(a*d-b*c)
    sp22=a*a+c*c-(b*b+d*d)
    sp23=-2.0*(a*b+c*d)
    sp31=2.0*(a*c+b*d)
    sp32=2.0*(a*b-c*d)
    sp33=a*a+d*d-(b*b+c*c)
    return numpy.matrix([[sp11,sp12,sp13], [sp21,sp22,sp23], [sp31,sp32,sp33]])

############################################################################## Clustering
#The cluster connectivity is saved in the "group dictionary" as a tree structure.
#The value of the group dictionary, group[i], indicates:
#group[i]>=0 ==> group[i] is the parent node for node i
#group[i]<0  ==> i is the root node; -group[i] is number of nodes in the same tree.

#x: node label
#group[]: group dictionary
#return value: root node of the group.
def MyGroup(x,group):
    while group[x] >= 0:
        x = group[x]
    return x


#register the nodes x and y as connected
def BindNodes(x,y,group):
    xg = MyGroup(x,group)
    yg = MyGroup(y,group)
    if xg != yg:
        #merge the trees
        group[yg] += group[xg]
        group[xg] =  yg


##################################################### Adjacency by distance and direction
#determine whether vector points to the direction
def IsAdjacent( vec, direc, thres ):
    siz = numpy.linalg.norm(vec)
    if siz < thres:
        #distance is short enough
        ip  = numpy.dot(vec, direc)
    if ip < -siz*0.95 or siz*0.95 < ip:
        #the vector directs
        return True
    return False


############################################################### Periodic boundary utility
#relative position vector at the periodic boundary condition
def Wrap( vector, box ):
    for dim in range(len(vector)):
        vector[dim] -= math.floor( vector[dim] / box[dim] + 0.5 ) * box[dim]
    return vector


################################################################################## Loader
#load a specific file type of molecular coordinate
def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    coms = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        x,y,z = map(float, columns[:3])
        com = numpy.array([x,y,z])
        coms.append(com)
    return coms



#return value: array of 7-element lists.
#7 elements = 3 for coordinates, 4 for quaternions.
def Configure(file):
    com = []  #default
    box = []
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        columns = line.split()
        if len(columns) > 0:
            if columns[0] == "@BOX3":
                line = file.readline()
                box = numpy.array(map(float,line.split()))
            elif columns[0] in ("@AR3A", "@NX4A"):
                com = LoadAR3A(file)
    return com,box


def decompose_water(waters):
    com = []
    h1  = []
    h2  = []
    for i in range(len(waters)):
        water= waters[i]
        com.append(water[0])
        h1.append(Wrap(water[1]-water[0],box))
        h2.append(Wrap(water[2]-water[0],box))
    return com,h1,h2

def Configure_gro(file):
    line = file.readline()
    if len(line) == 0:  #end of file detected:
        sys.exit(0)
    line = file.readline()
    nsite = int(line)
    waters = []
    water = []
    for i in range(nsite):
        line = file.readline()
        molnum = line[0:5]
        molname = line[5:10]
        elemname = line[10:15]
        sitenum = line[15:20]
        x = float(line[20:28])*10
        y = float(line[28:36])*10
        z = float(line[36:44])*10
        xyz = numpy.array([x,y,z])
        if elemname == "   OW":
            water.append(xyz)
        elif elemname == "  HW1":
            water.append(xyz)
        elif elemname == "  HW2":
            water.append(xyz)
            waters.append(water)
            water = []
    line = file.readline()
    box = line.split()
    box[0] = float(box[0])*10
    box[1] = float(box[1])*10
    box[2] = float(box[2])*10
    box = numpy.array(box)
    com,h1,h2 = decompose_water(waters)
    return com, box
            

def rint(x):
    return math.floor(x+0.5)



#assume xyz and box are numpy.array
def pairlist_small(memb,xyz,box):
    neighborset = dict()
    for i,j in itertools.combinations(memb,2):
        moli = xyz[i]
        molj = xyz[j]
        d = moli-molj
        rr = 0.0
        for k in range(3):
            d[k] -= rint( d[k] / box[k] ) * box[k]
            rr += d[k]**2
        r = math.sqrt(rr)
        if not neighborset.has_key(i):
            neighborset[i] = dict()
        if not neighborset.has_key(j):
            neighborset[j] = dict()
        neighborset[i][j] = r
        neighborset[j][i] = r
    return neighborset


#topolはあるノードに隣接するノードのリストを値とする辞書。
#いずれか最初のノードに+1のパリティをあたえ、以後隣接するごとに
#偶奇を反転する。既にパリティが与えられている点で矛盾が生じれば
#打ち切りNoneを返す。
def set_parity(topol):
    def next_parity(parity,n, value):
        if parity.has_key(n):
            return parity[n] == value
        else:
            parity[n] = value
            result = True
            for nn in topol[n]:
                result = result and next_parity(parity,nn,-value)
            return result
    first = topol.keys()[0]
    parity = dict()
    parity[first] = +1
    result = True
    for n in topol[first]:
        result = result and next_parity(parity,n,-1)
    if not result:
        return False
    else:
        return parity



def draw_network(hbn,com,box):
    print "@ 3"
    print "y 2"
    for i,j in hbn:
        if i < j:
            d = Wrap(com[i] - com[j], box)
            c = Wrap(com[j],box)
            print "l",
            for k in range(3):
                print c[k],
            for k in range(3):
                print c[k]+d[k],
            print



def draw_water(com,h1,h2,label,box):
    print "@ 2"
    print "y 1"
    for i in range(len(com)):
        c = com[i]
        cw = Wrap(c,box)
        print "r 0.5"
        print "c",
        for k in range(3):
            print cw[k],
        print
        print "r 0.2"
        print "s",
        for k in range(3):
            print cw[k],
        for k in range(3):
            print cw[k]+h1[i][k],
        print
        print "s",
        for k in range(3):
            print cw[k],
        for k in range(3):
            print cw[k]+h2[i][k],
        print
        print "c",
        for k in range(3):
            print cw[k]+h1[i][k],
        print
        print "c",
        for k in range(3):
            print cw[k]+h2[i][k],
        print
    print "@ 4"
    print "y 3"
    for i in range(len(com)):
        c = com[i]
        cw = Wrap(c,box)
        print "t",
        for k in range(3):
            print cw[k],
        print label[i]
                


def distance(d,box):
    s = 0.0
    for k in range(3):
        s +=  (d[k] - rint( d[k] / box[k] ) * box[k]) **2
    return math.sqrt(s)
    
    

def hbnetwork(pairs,com,h1,h2,box,hblen):
    hbn = set()
    for i,j,r in pairs:
        d1 = distance(com[j]+h1[j] - com[i],box)
        d2 = distance(com[j]+h2[j] - com[i],box)
        a1 = distance(com[i]+h1[i] - com[j],box)
        a2 = distance(com[i]+h2[i] - com[j],box)
        if d2 < d1:
            d1=d2
        if a2 < a1:
            a1 = a2
        if a1 < hblen or d1 < hblen:
            hbn.add((i,j))  #undirected network
            hbn.add((j,i))  #undirected network
    return hbn



def main(debug=False):
    #stage 1: load the structure
    #waters,box = Configure_gro(sys.stdin)
    com,box = Configure(sys.stdin)
    #draw_water(com,h1,h2,label,box)

    if len(com) ==0:
        sys.exit(0)
    if debug:
        print com
    #stage 2: determine the double lattices
    thres = 3.2 #Å; threshold for nearest 8 neighbors
    if len(sys.argv) > 1:
        thres = float(sys.argv[1])

    #pairlist_fine returns a dict() with key=labels of nearest neighbor pairs within the distance rc
    #and with value=distance between the two nodes
    pairs = pairlist.pairlist_fine(com,thres,box)
    print "@NGPH"
    print len(com)
    for i,j,d in pairs:
        print i,j
    print "-1 -1"

while True:
    main()
