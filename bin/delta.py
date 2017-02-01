#!/usr/bin/env python
#estimate the cell shape from match2 results
#(prototype)

import pairlist as pl
import sys
import numpy as np

points = []
for line in sys.stdin:
    cols = line.split()
    cols[0] = int(cols[0])
    for i in range(1,5):
        cols[i] = float(cols[i])
    if cols[4] < 10:
        points.append(cols[1:4])

points = np.array(points)
#print(points.shape)
box = np.array([40.1046, 39.2223, 36.4843])

pairs = pl.pairlist_fine(points, 8, box)
for i,j,L in pairs:
    p1 = points[i]
    p2 = points[j]
    d = p2 - p1
    d -= np.floor( d / box + 0.5 ) * box
    print d[0],d[1],d[2], L

