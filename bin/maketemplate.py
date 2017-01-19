#/usr/bin/env python
# coding: utf-8 

# make matching template
# 回転、並進、鏡映をオプションで選べるようにする。
#並進は必ず最初に行う。鏡映や回転はもはや周期境界条件をみたさないのであとで行う。
#引数1: 半径
#引数2-4: 並進 (並進しない場合は0みっつ)
#引数5: 対称操作 m 鏡映 r 回転 mr 回映
#引数6-8: (引数5を指定した場合) 対称軸または法線ベクトル
#引数9: (回転または回映の場合) 回転角度(degree)

import numpy
import math
import rotation_numpy



def LoadAR3A(file):
    line = file.readline()
    nmol = int(line)
    mols = []
    for i in range(nmol):
        line = file.readline()
        columns = line.split()
        x,y,z = map(float, columns)
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
            elif columns[0] =="@AR3A":
                mols = LoadAR3A(file)
    return mols,box



def Wrap( vector, box ):
    return vector - numpy.floor( vector / box + 0.5 ) * box




import sys

radius = float(sys.argv[1])
slide  = numpy.array([float(x) for x in sys.argv[2:5]])
command = ""
if len(sys.argv) > 5:
    command = sys.argv[5]
    pivot   = numpy.array([float(x) for x in sys.argv[6:9]])
    pivot /= numpy.linalg.norm(pivot)
    if command in ("r", "mr", "rm"):
        angle = float(sys.argv[9]) * math.pi / 180.0

mols,box = Configure(sys.stdin)

#slide
for mol in mols:
    mol += slide
    mol = Wrap(mol,box)

#rotate
if command in ("r", "mr", "rm"):
    sys.stderr.write("Rotating %s %s" % (pivot,angle))
    #四元数
    a = math.cos(angle/2.0)
    b = pivot[0] * math.sin(angle/2.0)
    c = pivot[1] * math.sin(angle/2.0)
    d = pivot[2] * math.sin(angle/2.0)
    q = numpy.array([a,b,c,d])
    rot = rotation_numpy.quat2rotmat(q)
    newmols = []
    for mol in mols:
        newmols.append(numpy.squeeze(numpy.asarray(numpy.dot(rot,mol))))
    mols = newmols

if command in ("m", "mr", "rm"):
    sys.stderr.write("Mirroring %s" % pivot)
    for mol in mols:
        mol -= 2*pivot*(numpy.dot(pivot,mol))

newmol = []
for mol in mols:
    if numpy.linalg.norm(mol) < radius:
        newmol.append(mol)

print "@AR3A"
print len(newmol)
for mol in newmol:
    print mol[0],mol[1],mol[2]



       


