#!/usr/bin/env python
#coding: utf-8
# slide and overlay the lattice manually.
#slide-and-overlay.F90の出力を読みこんで、可視化する部分だけを担うことにする。

import numpy
import numpy.linalg
import math
import sys
import itertools
import random

#import pairlist


#!/usr/bin/env python

#pairlist module
import math
import itertools

def rint(x):
    return math.floor(x+0.5)




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
def LoadNGPH(file):
    line = file.readline()
    #print line,
    n = int(line)
    network = set()
    while True:
        line = file.readline()
        xyz = line.split()
        #print xyz
        xyz = map(int,xyz)
        if xyz[0] < 0:
            return network
        network.add((xyz[0],xyz[1]))
        network.add((xyz[1],xyz[0]))


#load a specific file type of molecular coordinate
def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    coms = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        x,y,z = map(float, columns)
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
            elif columns[0].find("@AR3A")==0:
                com = LoadAR3A(file)
            elif columns[0].find("@NGPH")==0:
                network = LoadNGPH(file)
    return com,box,network



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


def distance(d,box):
    return math.sqrt(sqdistance(d,box))


def sqdistance(d,box):
    s = 0.0
    for k in range(3):
        s +=  (d[k] - rint( d[k] / box[k] ) * box[k]) **2
    return s
    



def draw1(com,box,hue,rad):
    for x,y,z in com:
        if -5 < z < 5:
            fill(hue, (z+5)/10, 1.0)
            ellipse(x-rad,y-rad,rad*2,rad*2)


import random

def trial(slide):
    com2 = [Wrap(com[i]+slide,box) for i in range(len(com))]
    pairs = pairlist_hetero(com0,com2,3.0,box,box)
    nearest= [(-1, 9999999.999) for i in range(len(com0))]
    for i,j in pairs:
        d = sqdistance(com0[i]-com2[j],box)
        if d < nearest[i][1]:
            nearest[i] = (j,d)
    sum = 0.0
    for i in range(len(com0)):
        j = nearest[i][0]
        if j >= 0:
            sum += nearest[i][1]
    return sum


def drawbox(X,Y,Z):
    ran = (0,1)
    div = ran[1] - ran[0]
    print "y 10"
    print "@ 3"
    print "r .3"
    print "c",
    e = ran[1]*(X+Y+Z)
    for i in range(3):
        print e[i],
    print
    for y in range(ran[0],ran[1]+1):
        for z in range(ran[0],ran[1]+1):
            s = (ran[0])*X+(y)*Y+(z)*Z
            e = s + X*div
            print "l",
            for i in range(3):
                print s[i],
            for i in range(3):
                print e[i],
            print
    print "y 11"
    print "@ 4"
    for z in range(ran[0],ran[1]+1):
        for x in range(ran[0],ran[1]+1):
            s = (x)*X+(ran[0])*Y+(z)*Z
            e = s + Y*div
            print "l",
            for i in range(3):
                print s[i],
            for i in range(3):
                print e[i],
            print
    print "y 12"
    print "@ 5"
    for x in range(ran[0],ran[1]+1):
        for y in range(ran[0],ran[1]+1):
            print "l",
            s = (x)*X+(y)*Y+(ran[0])*Z
            e = s + Z*div
            for i in range(3):
                print s[i],
            for i in range(3):
                print e[i],
            print


outputAR3R = False
if sys.argv[1] == "-A":
    outputAR3R = True
    del sys.argv[1]

if len(sys.argv) > 2:
    A = numpy.array([float(x) for x in sys.argv[2:5]])
    B = numpy.array([float(x) for x in sys.argv[5:8]])
    C = numpy.array([float(x) for x in sys.argv[8:11]])

PRE  = numpy.zeros(3)

MAT  = numpy.column_stack((A,B,C))
INV  = numpy.linalg.inv(MAT)

com,box,network = Configure(sys.stdin)

nnei = [0 for i in range(len(com))]
for i,j in network:
    nnei[i] += 1
#    nnei[j] += 1

AL = distance(A,box)
BL = distance(B,box)
CL = distance(C,box)

#pre-offset
for xyz in com:
    xyz += PRE


#draw box
if outputAR3R:
    print "@BOX9"
    for v in (A,B,C):
        for k in (0,1,2):
            print v[k],
        print
else:
    drawbox(A,B,C)
    print "r 0.2"
file = open(sys.argv[1])
lines = 0
ndef = 0.
ndrawn = 0
for line in file:
    #read *.slide file
    columns = [float(x) for x in line.split()]
    #match2: column0=molID, column1-3=displace, column4=error
    #pickup only good scores
    if columns[4] < 30:
        print "###",columns[4]
        lines += 1
        members = set()
        coord = []
        shift = numpy.array(columns[1:4])
        #ice rule check
        iceruleexception = 0
        inrange = 0.
        unitmols = []
        for i in range(len(com)):
            xyz = com[i]
            pos = Wrap(xyz - shift, box)
            #posが菱面体の中に含まれれば出力する。
            #菱面体の逆変換行列で単位立方体におさめることができる。
            relpos = numpy.dot(INV,pos)
            #それより、照合した8Å内を重ねるほうが正しい。
#            if 0<relpos[0]<1 and 0<relpos[1]<1 and 0<relpos[2]<1:
            if numpy.linalg.norm(pos) < 8.0:
                unitmols.append(i)
                inrange += 1
                if nnei[i] != 4:
                    iceruleexception += 1
        ndef += iceruleexception
        print "#",iceruleexception,inrange, ndef/lines
        if True:
        #if iceruleexception <= 4 and 25 <= inrange:
            print "##",unitmols
            ndrawn += 1
            for i in range(len(com)):
                xyz = com[i]
                pos = Wrap(xyz - shift, box)
                #posが菱面体の中に含まれれば出力する。
                #菱面体の逆変換行列で単位立方体におさめることができる。
                relpos = numpy.dot(INV,pos)
                #if 0<relpos[0]<1 and 0<relpos[1]<1 and 0<relpos[2]<1:
                #それより、照合した8Å内を重ねるほうが正しい。
                if outputAR3R:
                    if 0<relpos[0]<1 and 0<relpos[1]<1 and 0<relpos[2]<1:
                        coord.append([relpos[0],relpos[1],relpos[2]])
                else:
                    if -0.2<relpos[0]<1.2 and -0.2<relpos[1]<1.2 and -0.2<relpos[2]<1.2:
                    #if numpy.linalg.norm(pos) < 12.0:
                        print "@",nnei[i]
                        print "c",pos[0],pos[1],pos[2]
                        print "@ 3"
                        print "#",relpos[0],relpos[1],relpos[2]
                        for j in members:
                            if (i,j) in network:
                                delta = Wrap(com[j]-com[i],box)
                                print "l",
                                for k in range(3):
                                    print pos[k],
                                for k in range(3):
                                    print pos[k]+delta[k],
                                print
                        members.add(i)
        if outputAR3R:
            print "@AR3R"
            print len(coord)
            for r in coord:
                print r[0],r[1],r[2]
#        if ndrawn >= 3:
#            break
