#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#clustering.pyの出力を整理し、
#どこにどれぐらいのクラスターがあるか(grid-cluster.pyと同じ)
#どことどこの間に結合がたくさんあるか
#を出力する。


import sys
import numpy as np
import grid as gr
import yaplot as yp


#Simple and quick grouping algorithm
#説明はとても面倒くさいので省略。
def mygroup(x,group):
    while type(group[x]) is tuple:
        x = group[x]
    return x


def mergegroups(x,y,group):
    xg = mygroup(x,group)
    yg = mygroup(y,group)
    if xg != yg:
        group[yg]   += group[xg]
        group[xg] = yg

def drawbox(X,Y,Z):
    ran = (0,1)
    div = ran[1] - ran[0]
    t = yp.layer(10)
    t += yp.palette(3)
    t += yp.radius(.3)
    e = ran[1]*(X+Y+Z)
    t += yp.circle(*e)
    for y in range(ran[0],ran[1]+1):
        for z in range(ran[0],ran[1]+1):
            s = (ran[0])*X+(y)*Y+(z)*Z
            e = s + X*div
            t += yp.line(*s,*e)
    t += yp.layer(11)
    t += yp.palette(4)
    for z in range(ran[0],ran[1]+1):
        for x in range(ran[0],ran[1]+1):
            s = (x)*X+(ran[0])*Y+(z)*Z
            e = s + Y*div
            t += yp.line(*s,*e)
    t += yp.layer(12)
    t += yp.palette(5)
    for x in range(ran[0],ran[1]+1):
        for y in range(ran[0],ran[1]+1):
            s = (x)*X+(y)*Y+(ran[0])*Z
            e = s + Z*div
            t += yp.line(*s,*e)
    return t

file = sys.stdin
A = np.array([float(x) for x in sys.argv[1:4]])
B = np.array([float(x) for x in sys.argv[4:7]])
C = np.array([float(x) for x in sys.argv[7:10]])
shift = np.array([float(x) for x in sys.argv[10:13]])
MAT  = np.array([A,B,C])

NGrid = 24
vertices = dict()
gridsize = np.array((NGrid,NGrid,NGrid))
grid = np.zeros((NGrid,NGrid,NGrid))
N = int(file.readline())
for i in range(N):
    x,y,z,v = [int(p) for p in file.readline().split()]
    vertices[(x,y,z)] = v
    grid[x,y,z] = v

#g = gr.Contour(grid)
#flakes = g.contour_flakes(10)
#print(g.contour_yaplot(flakes))
#sys.exit(0)

#clustering of the grid points
queue = list(vertices.keys())
done = set()
group = dict()
for p in vertices:
    group[p] = -vertices[p]  #solo group

MinPop = 10
while len(queue):
    p = queue.pop(0)
    if p not in done:
        done.add(p)
        if vertices[p] >= MinPop:
            nei = ((p[0]+1)%NGrid, p[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = ((p[0]-1+NGrid)%NGrid, p[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], (p[1]+1)%NGrid, p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], (p[1]-1+NGrid)%NGrid, p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], p[1], (p[2]+1)%NGrid)
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], p[1], (p[2]-1+NGrid)%NGrid)
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)

#estimate the com of each cluster
coms = dict()
nums = dict()
for p in vertices:
    v = vertices[p]
    q = mygroup(p, group) #parent node
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    dz = p[2] - q[2]
    dx = (dx + NGrid + NGrid//2) % NGrid - NGrid//2
    dy = (dy + NGrid + NGrid//2) % NGrid - NGrid//2
    dz = (dz + NGrid + NGrid//2) % NGrid - NGrid//2
    if q not in coms:
        coms[q] = np.zeros(3)
        nums[q] = 0
    coms[q] += np.array([dx,dy,dz])*v
    nums[q] += v

for p in coms:
    coms[p] /= nums[p]  #displacement from the parent node to the com

print(drawbox(A,B,C), end="")

#verify
s = yp.radius(0.5)
s += yp.palette(3)
for p in coms:
    if nums[p] > 100:
        atom = (np.array(p)+coms[p]) / gridsize + shift
        atom -= np.floor(atom)
        atom = np.dot(atom, MAT)
        s += yp.circle(*atom)
print(s,end="")
#sys.exit(0)

bonds = dict()
N = int(file.readline())
for i in range(N):
    x,y,z,a,b,c,v = [int(p) for p in file.readline().split()]
    if (x,y,z) in group and (a,b,c) in group:
        g1 = mygroup((x,y,z), group)
        g2 = mygroup((a,b,c), group)
        g = frozenset((g1,g2))
        if g not in bonds:
            bonds[g] = 0
        bonds[g] += v

print(yp.palette(2),end="")
for bond in bonds:
    g1,g2 = bond
    if -group[g1] >= 100 and -group[g2] >= 100:
        r = bonds[bond]/5000
        if r > 0.011:
            print("r",r)
            p1 = np.array(g1) + coms[g1]
            p2 = np.array(g2) + coms[g2]
            d  = p2 - p1
            d -= np.floor( d / gridsize + 0.5) * gridsize
            p1 = p1/gridsize + shift
            p1 -= np.floor(p1)
            d /= gridsize
            p2 = p1 + d
            p1 = np.dot(p1,MAT)
            p2 = np.dot(p2,MAT)
            print("s", *p1, *p2)
            #print(g1,g2,bonds[bond])
