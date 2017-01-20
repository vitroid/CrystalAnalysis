#!/usr/bin/env python

import numpy

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



div = 20

import sys
grid = dict()
file = sys.stdin
shift = numpy.zeros(3)
if len(sys.argv) > 1:
    shift = numpy.array([float(x) for x in sys.argv[1:4]])
natom = 0
while True:
    line = file.readline()
    if len(line) == 0:
        break
    columns = line.split()
    if len(columns) > 0:
        if columns[0] == "@AR3R":
            coms = LoadAR3A(file)
            for com in coms:
                com += shift
                com -= numpy.floor(com)
                i,j,k = [int(x*div) for x in com]
                grid[(i,j,k)] = grid.get((i,j,k),0) + 1
                natom += 1.0

avgdens = natom / div**3
print "@GRID"
print div,div,div
for i in range(div):
    for j in range(div):
        for k in range(div):
            print grid.get((i,j,k),0) / avgdens


                
