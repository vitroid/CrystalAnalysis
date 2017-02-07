#!/usr/bin/env python
#estimate the cell shape from match2 results
#(prototype)

import pairlist as pl
import sys
import numpy as np

points = []
scores = []
for line in sys.stdin:
    cols = line.split()
    cols[0] = int(cols[0])
    for i in range(1,5):
        cols[i] = float(cols[i])
    if cols[4] < 15:
        points.append(cols[1:4])
	scores.append(cols[4])

points = np.array(points)
#print(points.shape)
file = open(sys.argv[1]) #assume .ar3a file or .nx4a file
while True:
    line = file.readline()
    if len(line) == 0:
        break
    cols = line.split()
    if len(cols) >= 1 and cols[0] == "@BOX3":
        line = file.readline()
        box = np.array([float(x) for x in line.split()[:3]])
        break

pairs = pl.pairlist_fine(points, 15, box)
for i,j,L in pairs:
    p1 = points[i]
    p2 = points[j]
    d = p2 - p1
    d -= np.floor( d / box + 0.5 ) * box
    print d[0],d[1],d[2], L, scores[i]*scores[j]

