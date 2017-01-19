#!/usr/bin/env python
import sys
import numpy
import math


def readNGPH(file):
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
            return n,network
        network.add((xyz[0],xyz[1]))

def readRNGS(file):
    line = file.readline()
    #print line,
    n = int(line)
    rings = dict()
    while True:
        line = file.readline()
        xyz = line.split()
        #print xyz
        xyz = map(int,xyz)
        if xyz[0] == 0:
            return n,rings
        size = xyz.pop(0)
        if not rings.has_key(size):
            rings[size] = set()
        rings[size].add(tuple(xyz))

def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    mols = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        x,y,z = map(float, columns[:3])
        com = numpy.array([x,y,z])
        mols.append(com)
    return mols



#return value: array of 7-element lists.
#7 elements = 3 for coordinates, 4 for quaternions.
def Configure(file):
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
                mols = LoadAR3A(file)
            elif columns[0] =="@RNGS":
                nmol,rings = readRNGS(file)
    return mols,box,rings



def Wrap( vector, box ):
    for dim in range(len(vector)):
        vector[dim] -= math.floor( vector[dim] / box[dim] + 0.5 ) * box[dim]
    return vector


file = sys.stdin
mols,box,rings = Configure(file)

for size in rings:
    print "@",size
    print "y",size
    for ring in rings[size]:
        for j in range(len(ring)):
            ri = mols[ring[j-1]]
            rj = mols[ring[j]]
            d = Wrap(rj-ri,box)
            print "l",
            for k in range(3):
                print ri[k],
            for k in range(3):
                print ri[k]+d[k],
            print
print  # frame separator
