#!/usr/bin/env python
#coding: utf-8

#
import numpy as np
import sys
import logging



################################################################################## Loader
def LoadNGPH(file):
    line = file.readline()
    #print line,
    n = int(line)
    neighbor = [[] for i in range(n)]
    while True:
        line = file.readline()
        ij = [int(x) for x in line.split()]
        if ij[0] < 0:
            return neighbor
        neighbor[ij[0]].append(ij[1])
        neighbor[ij[1]].append(ij[0])


#load a specific file type of molecular coordinate
def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    coms = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        com = np.array([float(x) for x in columns[:3]])
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
                box = np.array([float(x) for x in line.split()])
            elif columns[0].find("@AR3A")==0:
                com = LoadAR3A(file)
            elif columns[0].find("@NGPH")==0:
                network = LoadNGPH(file)
    return com,box,network


def Wrap(r, box):
    return r - np.floor( r / box + 0.5 ) * box

def relpos_to_grid(relpos, gridsize):
    ipos = relpos*gridsize
    return tuple([int(x) for x in ipos])


def add_bond(relpos1, relpos2, gridsize, bonds, gshift):
    logger = logging.getLogger()
    #logger.debug("gshift {0}".format(gshift))
    #logger.debug("relpos1 {0} {1}".format(relpos1,relpos2))
    rel1 = relpos1 + gshift
    rel1 -= np.floor(rel1)
    rel2 = relpos2 + gshift
    rel2 -= np.floor(rel2)
    ipos1 = relpos_to_grid(rel1, gridsize)
    ipos2 = relpos_to_grid(rel2, gridsize)
    p = frozenset((ipos1,ipos2))
    #logger.debug("p {0}".format(p))
    if len(p) == 2:
        if p not in bonds:
            bonds[p] = 0
        bonds[p] += 1

debug=True
if debug:
    logging.basicConfig(level=logging.DEBUG,
                        #filename='log.txt',
                        format="%(asctime)s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

unitinfo = open(sys.argv[2])  #unitinfo
A=None
B=None
C=None
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
        elif cols[0] == "@DSPL":
            gshift = np.array([float(x) for x in unitinfo.readline().split()])

Threshold = float(sys.argv[3])
NGrid = int(sys.argv[4])
#grid for vertices
gridsize=(NGrid,NGrid,NGrid)
#

PRE  = np.zeros(3)

MAT  = np.column_stack((A,B,C))
INV  = np.linalg.inv(MAT)

com,box,neighbors = Configure(sys.stdin)


AL = np.linalg.norm(A)
BL = np.linalg.norm(B)
CL = np.linalg.norm(C)

#pre-offset
for xyz in com:
    xyz += PRE

bonds = dict()
debug = False
if debug:
    logging.basicConfig(level=logging.DEBUG,
                #filename='log.txt',
            format="%(asctime)s %(levelname)s %(message)s")
else:
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger()

file = open(sys.argv[1])#match2

count = 0
for line in file:
    #read *.slide file
    columns = [float(x) for x in line.split()]
    #match2: column0=molID, column1-3=displace, column4=error
    #pickup only good scores
    if columns[4] < Threshold:
        logger.debug(columns)
        count += 1
        #if count == 10:
    #        break
        shift = np.array(columns[1:4])
        relpos = np.zeros_like(com)
        incell = set()
        for i in range(len(com)):
            xyz = com[i]
            pos = Wrap(xyz - shift, box)
            relpos[i] = np.dot(INV,pos)
            b = (0<relpos[i,0]<1 and 0<relpos[i,1]<1 and 0<relpos[i,2]<1)
            if b:
                incell.add(i)
        for i in incell:
            for j in neighbors[i]:
                if j in incell:
                    add_bond(relpos[i], relpos[j], gridsize, bonds, gshift)
                else:
                    p = relpos[j]
                    rp = p - np.floor(p) #put in the box
                    add_bond(relpos[i], rp, gridsize, bonds, gshift)

#この読みこみだけでけっこう時間がかかるので、一旦結果を出力する。
print("@GBND")
print(NGrid,NGrid,NGrid)
for bond in bonds:
    p1,p2 = bond
    print(*p1,*p2,bonds[bond]/count)  #Average number of bonds in a frame
print(-1,-1,-1,-1,-1,-1,-1)
