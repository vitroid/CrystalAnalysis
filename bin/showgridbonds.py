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
import logging

debug = True
if debug:
    logging.basicConfig(level=logging.DEBUG,
                #filename='log.txt',
            format="%(asctime)s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s")

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


logger = logging.getLogger()
debug=True
if debug:
        logging.basicConfig(level=logging.DEBUG,
                            #filename='log.txt',
                            format="%(asctime)s %(levelname)s %(message)s")
else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")

mode = "yaplot"
if len(sys.argv) > 3:
    if sys.argv[1] == "-s":
        mode = "openscad"
        #Prepare in Angdtrom scale with spheres of radius 1.5,
        #And scale all to let the sphere diameter be 15 mm for space-filling,
        #12 mm for B&S model, i.e. Rm A radius
        print('use <bond.scad>;')
        print("$fn=40;")
        print("Rm=0.7;")
        print("Rb=0.6;")
        Rm=0.7
        Rb=0.6
        print("scale([5, 5, 5]){{")
        print("intersection(){{")
    else:
        sys.exit(1)
    sys.argv.pop(1)
unitinfo = open(sys.argv[1])
A=None
B=None
C=None
#shift=None
while True:
    line = unitinfo.readline()
    if len(line) == 0:
        break
    cols = line.split()
    if len(cols) > 0:
        if cols[0] == "@BOX9":
            A = np.array([float(x) for x in unitinfo.readline().split()])
            B = np.array([float(x) for x in unitinfo.readline().split()])
            C = np.array([float(x) for x in unitinfo.readline().split()])
        #elif cols[0] == "@DSPL":
        #    shift = np.array([float(x) for x in unitinfo.readline().split()])
MAT  = np.array([A,B,C])


#Note it is already shifted by the unitinfo.
avggrid = open(sys.argv[2])
while True:
    line = avggrid.readline()
    if len(line) == 0:
        break
    cols = line.split()
    if cols[0] == "@GRID":
        gridsize = tuple([int(x) for x in avggrid.readline().split()])
        grid = np.zeros(gridsize)
        vertices = dict()
        for x in range(gridsize[0]):
            for y in range(gridsize[1]):
                for z in range(gridsize[2]):
                    grid[x,y,z] = float(avggrid.readline())
                    if grid[x,y,z] != 0:
                        #It is used for clustering and queueing
                        vertices[(x,y,z)] = grid[x,y,z]

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


#10 is the threshold for drawing the cloud in the avg.grid.yap, so it is reasonable.
MinPop = 10
#build the percolated clusters
while len(queue):
    p = queue.pop(0)
    if p not in done:
        done.add(p)
        if vertices[p] >= MinPop:
            nei = ((p[0]+1)%gridsize[0], p[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = ((p[0]-1+gridsize[0])%gridsize[0], p[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], (p[1]+1)%gridsize[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], (p[1]-1+gridsize[1])%gridsize[1], p[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], p[1], (p[2]+1)%gridsize[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)
            nei = (p[0], p[1], (p[2]-1+gridsize[2])%gridsize[2])
            if nei in vertices and vertices[nei] >= MinPop:
                mergegroups(p, nei, group)
                queue.append(nei)


#debug: it must recover the content of grid.clusters
for p in vertices:
    if type(group[p]) is not tuple and group[p] < -80:
        logger.debug("Vertex {0} {1}".format(p, -group[p]))
#sys.exit(0)



#estimate the com of each cluster
coms = dict()
nums = dict()
for p in vertices:
    v = vertices[p]
    q = mygroup(p, group) #parent node
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    dz = p[2] - q[2]
    dx = (dx + gridsize[0] + gridsize[0]//2) % gridsize[0] - gridsize[0]//2
    dy = (dy + gridsize[1] + gridsize[1]//2) % gridsize[1] - gridsize[1]//2
    dz = (dz + gridsize[2] + gridsize[2]//2) % gridsize[2] - gridsize[2]//2
    if q not in coms:
        coms[q] = np.zeros(3)
        nums[q] = 0
    coms[q] += np.array([dx,dy,dz])*v
    nums[q] += v

for p in coms:
    coms[p] /= nums[p]  #displacement from the parent node to the com

if mode == "yaplot":
    print(drawbox(A,B,C), end="")
else:
    logger.info("Assuming a rectangular box")
    AL = np.linalg.norm(A)
    BL = np.linalg.norm(B)
    CL = np.linalg.norm(C)
    print("cube([{0},{1},{2}]);".format(AL,BL,CL))
    print("union(){{");
    

#verify
#sys.exit(0)

file = sys.stdin  #*.gridbond
#Note that bonds are shifted in making the gridbond.
bonds = dict()
while True:
    line = file.readline()
    if len(line) == 0:
        break
    cols = line.split()
    if cols[0] == "@GBND":
        gridsize2 = tuple([int(x) for x in file.readline().split()])
        assert gridsize == gridsize2
        while True:
            cols = file.readline().split()
            x,y,z,a,b,c = [int(v) for v in cols[:6]]
            v = float(cols[6])
            if x < 0:  #terminator
                break
            if (x,y,z) in group and (a,b,c) in group:
                #assign each end of the bond to a group
                g1 = mygroup((x,y,z), group)
                g2 = mygroup((a,b,c), group)
                if g1 == g2:
                    continue
                g = frozenset((g1,g2))
                if g not in bonds:
                    bonds[g] = 0
                bonds[g] += v


NN = dict()
s = yp.palette(2)
for bond in bonds:
    g1,g2 = bond
    if True: #-group[g1] >= 100 and -group[g2] >= 100:
        r = bonds[bond]/10
        if bonds[bond] > 0.85:
            logger.info("bond {0} {1}".format(bond,bonds[bond]))
            
            s += yp.radius(r)
            p1 = (np.array(g1) + coms[g1]) / gridsize
            p2 = (np.array(g2) + coms[g2]) / gridsize
            d  = p2 - p1
            d -= np.floor( d + 0.5)
            #p1 += shift
            p1 -= np.floor(p1)
            p2 = p1 + d
            if mode == "openscad":
                if bonds[bond] > 1.0: #thick bonds
                    for ix in range(-1,2):
                        for iy in range(-1,2):
                            for iz in range(-1,2):
                                jx = (p1[0]+ix)*AL
                                jy = (p1[1]+iy)*BL
                                jz = (p1[2]+iz)*CL
                                kx = (p2[0]+ix)*AL
                                ky = (p2[1]+iy)*BL
                                kz = (p2[2]+iz)*CL
                                if ((-Rb < jx < AL+Rb or -Rb < kx < AL+Rb) and
                                    (-Rb < jy < BL+Rb or -Rb < ky < BL+Rb) and
                                    (-Rb < jz < CL+Rb or -Rb < kz < CL+Rb)):
                                    print("bond([{0},{1},{2}],[{3},{4},{5}],r=Rb);"
                                        .format(jx,jy,jz,kx,ky,kz))
            else:
                p1 = np.dot(p1,MAT)
                p2 = np.dot(p2,MAT)
                s += yp.stick(*p1, *p2)
                if bonds[bond] > 0.5: #thick bonds
                    if g1 not in NN:
                        NN[g1] = 0
                    if g2 not in NN:
                        NN[g2] = 0
                    NN[g1] += 1
                    NN[g2] += 1
                    
#atoms
s += yp.radius(0.5)
for p in coms:
    if nums[p] > 80:  #This depends on the gridsize. 80 is suitable for 24x24x24.
        atom = (np.array(p)+coms[p]) / gridsize #+ shift
        atom -= np.floor(atom)   #0..1
        if mode == "openscad":
            for ix in range(-1,2):
                for iy in range(-1,2):
                    for iz in range(-1,2):
                        jx = (atom[0]+ix)*AL
                        jy = (atom[1]+iy)*BL
                        jz = (atom[2]+iz)*CL
                        if -Rm < jx < AL+Rm and -Rm < jy < BL+Rm and -Rm < jz < CL+Rm:
                            print("translate([{0},{1},{2}]) sphere(r=Rm);".format(jx,jy,jz))
        else:
            if p in NN:
                if NN[p] == 4:
                    s += yp.palette(3)
                elif NN[p] < 4:
                    s += yp.palette(5)
                else:
                    s += yp.palette(4)
                atom = np.dot(atom, MAT)
                s += yp.circle(*atom)
#output and newpage
if mode == "yaplot":
    print(s)
else:
    print("}}//union");
    print("}}//intersection");
    print("}}//scale");
    
