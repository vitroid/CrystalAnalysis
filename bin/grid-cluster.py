#!/usr/bin/env python

#read a grid, make cluster, and determine their positions

def loadGRID(file):
    line = file.readline()
    nx,ny,nz = [int(x) for x in line.split()]
    grid = dict()
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                value = float(file.readline())
                if value != 0:
                    grid[(x,y,z)] = value
    return (nx,ny,nz),grid

#return a list of (position,value)
def percolate(pos,grid,flag):
    i,j,k = pos
    ri = (i+gridsize[0]) % gridsize[0]
    rj = (j+gridsize[1]) % gridsize[1]
    rk = (k+gridsize[2]) % gridsize[2]
    if (ri,rj,rk) in flag or not grid.has_key((ri,rj,rk)) or grid[(ri,rj,rk)] < 1:
        return []
    else:
        flag.add((ri,rj,rk))
        result = [(i,j,k,grid[(ri,rj,rk)])]
        result += percolate((i+1,j,k),grid,flag)
        result += percolate((i-1,j,k),grid,flag)
        result += percolate((i,j-1,k),grid,flag)
        result += percolate((i,j+1,k),grid,flag)
        result += percolate((i,j,k-1),grid,flag)
        result += percolate((i,j,k+1),grid,flag)
        return result

import sys
import numpy

file = sys.stdin
while True:
    line = file.readline()
    if len(line) == 0:
        break
    columns = line.split()
    if len(columns) > 0:
        if columns[0] == "@GRID":
            gridsize,grid = loadGRID(file)
            gridsize = numpy.array([float(i) for i in gridsize])


flag = set()
for pos in grid:
    if pos in flag:
        pass
    else:
        points = percolate(pos,grid,flag)
        if len(points) > 0:
            xs = 0.0
            ys = 0.0
            zs = 0.0
            vs = 0.0
            for point in points:
                x,y,z,v = point
                xs += x*v
                ys += y*v
                zs += z*v
                vs += v
            xs /= vs
            ys /= vs
            zs /= vs
            print xs/gridsize[0],ys/gridsize[1],zs/gridsize[2],vs,len(points)
