#!/usr/bin/env python

import numpy as np

#load a specific file type of molecular coordinate
def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    coms = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        x,y,z = map(float, columns)
        com = np.array([x,y,z])
        coms.append(com)
    return coms



import sys
grid = dict()
file = sys.stdin
div = int(sys.argv[1])
shift = np.zeros(3)
unitinfo = open(sys.argv[2])
while True:
    line = unitinfo.readline()
    if len(line) == 0:
        break
    cols = line.split()
    if len(cols) > 0:
        #if cols[0] == "@BOX9":
        #    A = np.array([float(x) for x in unitinfo.readline().split()])
        #    B = np.array([float(x) for x in unitinfo.readline().split()])
        #    C = np.array([float(x) for x in unitinfo.readline().split()])
        if cols[0] == "@DSPL":
            shift = np.array([float(x) for x in unitinfo.readline().split()])
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
                com -= np.floor(com)
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

