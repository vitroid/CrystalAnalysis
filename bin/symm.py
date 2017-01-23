#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Find the symmetry in the grid data.
import numpy as np
import sys

def loadGRID(file):
    line = file.readline()
    nx,ny,nz = [int(x) for x in line.split()]
    grid = np.zeros((nx,ny,nz))
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                value = float(file.readline())
                if value != 0:
                    grid[x,y,z] = value
    return (nx,ny,nz),grid


def main():
    file = sys.stdin
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        columns = line.split()
        if len(columns) > 0:
            if columns[0] == "@GRID":
                gridsize,grid = loadGRID(file)
                nx,ny,nz = gridsize

    maxscore = np.sum(grid*grid)
    grid =  np.roll(np.roll(np.roll(grid, 2, axis=0), 8, axis=1), 10, axis=2)
    #grid =  np.roll(grid, -4, axis=0)

    #原点にずらしてから，原点に関して対称操作を行うほうが直感的にはわかりやすいが，
    #対称操作を行ってから原点をずらす方が精密な照合ができる．
    #後者を行う場合には，表現方法を工夫する必要がある．
        

    #6 screw axis 90 deg
    #90度回転したので，原点は[-1,0,0]に動いた．
    rotated = np.rot90(grid)
    for sx in range(nx):
        for sy in range(ny):
            for sz in (nz/4, -nz/4):
                shifted =  np.roll(np.roll(np.roll(grid, sx, axis=0), sy, axis=1), sz, axis=2)
                #rotated = np.roll(np.roll(np.rot90(shifted, k=1)[:, :, ::-1], 1, axis=0), 1, axis=2)
                #print(shifted[0,0,0])
                #print(rotated[0,0,0])
                score = np.sum(shifted*rotated) /maxscore
                if score > 0.7:
                    #この場合，回転とshiftの結果の不動点が回転中心なのだが，それはどこか．
                    #It seems to be wrong.
                    cx = (nx-1-sx+sy)/2.0
                    cy = (ny-1-sx-sy)/2.0
                    print "6screw90 {0} {1} {2} {3}".format(cx, cy, sz, score)

    #7 glide reflection
    #There many possible ways....
    #7-1 translate in z/2 and reflect in x
    reflected = grid[::-1, :,: ]
    for sx in range(nx):
        shifted =  np.roll(np.roll(grid, sx, axis=0), nz/2, axis=2)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cx = (nx-1-sx)/2.0
            print "7glidez/2:x {0} {1}".format(cx, score)

    #7-2 translate in z/2 and reflect in y
    reflected = grid[:, ::-1,: ]
    for sy in range(ny):
        shifted =  np.roll(np.roll(grid, sy, axis=1), nz/2, axis=2)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cy = (ny-1-sy)/2.0
            print "7glidez/2:y {0} {1}".format(cy, score)

    #7-11 translate in x/2 and reflect in y
    reflected = grid[:, ::-1,: ]
    for sy in range(ny):
        shifted =  np.roll(np.roll(grid, sy, axis=1), nx/2, axis=0)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cy = (ny-1-sy)/2.0
            print "7glidex/2:y {0} {1}".format(cy, score)
                    
    #7-12 translate in x/2 and reflect in z
    reflected = grid[:, :,::-1 ]
    for sz in range(nz):
        shifted =  np.roll(np.roll(grid, sz, axis=2), nx/2, axis=0)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cz = (nz-1-sz)/2.0
            print "7glidex/2:z {0} {1}".format(cz, score)
                    
    #7-21 translate in y/2 and reflect in z
    reflected = grid[:, :,::-1 ]
    for sz in range(nz):
        shifted =  np.roll(np.roll(grid, sz, axis=2), ny/2, axis=1)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cz = (nz-1-sz)/2.0
            print "7glidey/2:z {0} {1}".format(cz, score)
                    
    #7-22 translate in y/2 and reflect in x
    reflected = grid[::-1, :,: ]
    for sx in range(nx):
        shifted =  np.roll(np.roll(grid, sx, axis=0), ny/2, axis=1)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cx = (nx-1-sx)/2.0
            print "7glidey/2:x {0} {1}".format(cx, score)
                    
    #3-3 rot z
    rotated = grid[::-1, ::-1, 0]
    for sx in range(nx):
        for sy in range(ny):
            shifted =  np.roll(np.roll(grid, sx, axis=0), sy, axis=1)
            score = np.sum(shifted*rotated) /maxscore
            if score > 0.3:
                #nx-1-x=x+sx
                print "rotz {0} {1} {2}".format((nx-1-sx)/2.0, (ny-1-sy)/2.0, score)

    #2 mirror
    #2-1 mirror x
    #原点は[-1,0,0]に移動した
    mirrored = grid[::-1, :, :]
    for s in range(nx+1):
        shifted = np.roll(grid, s, axis=0)
        score = np.sum(shifted*mirrored) / maxscore
        if score > 0.7:
            #nx-1-x=x+s
            print "refx {0} {1}".format((nx-1-s)/2.0, score)
            #周期境界なので実際には不動点は2倍ある．

    #2-2 mirror y
    #原点は[-1,0,0]に移動した
    mirrored = grid[:, ::-1, :]
    for s in range(ny+1):
        shifted = np.roll(grid, s, axis=1)
        score = np.sum(shifted*mirrored) / maxscore
        if score > 0.4:
            #ny-1-y=y+s
            print "refy {0} {1}".format((ny-1-s)/2.0, score)
            #周期境界なので実際には不動点は2倍ある．

    #4 symmetric centers
    #このreflectedは，全反転したので，原点の格子点が[-1,-1,-1]に動いている．
    reflected = grid[::-1, ::-1, ::-1]
    for sx in range(-1,nx+1):
        for sy in range(-1,ny+1):
            for sz in range(-1,nz+1):
                shifted = np.roll(np.roll(np.roll(grid, sx, axis=0), sy, axis=1), sz, axis=2)
                #原点を動かさないで反転．
                #reflected = np.roll(np.roll(np.roll(shifted[::-1, ::-1, ::-1], 1, axis=0), 1, axis=1), 1, axis=2)
                #print(shifted[0,0,0])
                #print(reflected[0,0,0])
                score = np.sum(shifted*reflected) /maxscore
                if score > 0.7:
                    #不動点が回転中心，のはず
                    print "center {0} {1} {2} {3}".format((nx-1-sx)/2.0, (ny-1-sy)/2.0, (nz-1-sz)/2.0, score)
                    #周期境界なので不動点は本当は8倍?

    sys.exit(0)


    
    #5 rotary reflection 90 deg
    #90度回転し，z方向に反転したので，原点は[-1,0,-1]に動いた．
    rotated = np.rot90(grid[:, :, ::-1])
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted =  np.roll(np.roll(np.roll(grid, sx, axis=0), sy, axis=1), sz, axis=2)
                #rotated = np.roll(np.roll(np.rot90(shifted, k=1)[:, :, ::-1], 1, axis=0), 1, axis=2)
                #print(shifted[0,0,0])
                #print(rotated[0,0,0])
                score = np.sum(shifted*rotated) /maxscore
                if score > 0.7:
                    #この場合，回転とshiftの結果の不動点が回転中心なのだが，それはどこか．
                    cx = (nx-1-sx+sy)/2.0
                    cy = (ny-1-sx-sy)/2.0
                    #nz-1-z = z+sz; (nz-1-sz)/2 = z;
                    cz = (nz-1-sz) / 2.0
                    print "rotrefz {0} {1} {2} {3}".format(cx, cy, cz, score)


    #2-4 xとyの交換=  x=yでの鏡映
    #原点は動かない．
    mirrored = np.transpose(grid, (1,0,2))
    for s in range(nx):
        shifted = np.roll(np.roll(grid, s, axis=0), -s, axis=1)
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.7:
            print "refxy {0} {1}".format(nx-s/2.0, score)





    #1 translation
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = np.roll(np.roll(np.roll(grid, sx, axis=0), sy, axis=1), sz, axis=2)
                score = np.sum(shifted*grid) / maxscore
                if score > 0.7:
                    print "trans {0} {1} {2} {3}".format(sx,sy,sz, score)

    sys.exit(0)
    
    #2-2 y
    for s in range(ny):
        shifted = np.roll(grid, s, axis=1)
        mirrored = shifted[:, ::-1, :]
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            print "refy {0} {1}".format(s, score)
    
    #2-3 z
    for s in range(nz):
        shifted = np.roll(grid, s, axis=2)
        mirrored = shifted[:, :, ::-1]
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            print "refz {0} {1}".format(s, score)


    #2-5 x=-y
    mirrored = np.transpose(grid[::-1,:,:], (1,0,2))
    for s in range(nx):
        shifted = np.roll(np.roll(grid[::-1,:,:], s, axis=0), -s, axis=1)
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            print "ref-xy {0} {1}".format(s, score)

    #3 rotation
    #3-1 x
    rotated = grid[0, ::-1, ::-1]
    for sy in range(ny):
        for sz in range(nz):
            shifted =  np.roll(np.roll(grid, sy, axis=1), sz, axis=2)
            score = np.sum(shifted*rotated) /maxscore
            if score > 0.3:
                print "rotx {0} {1} {2}".format(sy, sz, score)


    
main()


    
