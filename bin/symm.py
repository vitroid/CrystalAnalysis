#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Find the symmetry in the grid data.
import numpy as np
import sys
import logging
import contour



def yap_xplane_at(x):
    return "p 4 {0} 0 0 {0} 1 0 {0} 1 1 {0} 0 1".format(x)


def yap_yplane_at(y):
    return "p 4 0 {0} 0 0 {0} 1 1 {0} 1 1 {0} 0".format(y)



def main():
    logger = logging.getLogger()
    debug=True
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            #filename='log.txt',
                            format="%(asctime)s %(levelname)s %(message)s")
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
    yaplot = True
    file = sys.stdin
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        columns = line.split()
        if len(columns) > 0:
            if columns[0] == "@GRID":
                g = contour.PBCGrid(file=file)
                nx,ny,nz = g.grid.shape

    maxscore = np.sum(g.grid*g.grid)
    #g.grid =  np.roll(g.grid, -4, axis=0)

    #原点にずらしてから，原点に関して対称操作を行うほうが直感的にはわかりやすいが，
    #対称操作を行ってから原点をずらす方が精密な照合ができる．
    #後者を行う場合には，表現方法を工夫する必要がある．
        
    #7 glide reflection
    #There many possible ways....
    #7-2 translate in z/2 and reflect in y
    reflected = contour.PBCGrid()
    reflected.grid = g.grid[:, ::-1,: ]
    for sy in range(ny):
        shifted = contour.PBCGrid()
        shifted.grid =  np.roll(np.roll(g.grid, sy, axis=1), nz//2, axis=2)
        score = np.sum(shifted.grid*reflected.grid) /maxscore
        if score > 0.7:
            cy = (ny-1-sy)/2.0
            msg = "7glidez/2:y {0} {1}".format(cy, score)
            logger.info(msg)
            if yaplot:
                #direct action
                print("@ 2\nt 0 0 1.05 " + msg)
                print(yap_yplane_at((sy+cy)/ny))
                print("@ 0")
                flakes = reflected.contour_flakes(10)
                print(reflected.contour_yaplot(flakes), end="")
                print("@ 4")
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([0, sy, nz//2])
                print(g.contour_yaplot(flakes))
                #shifted expression
                print("@ 2\nt 0 0 1.05 " + msg)
                print("@ 0")
                print(reflected.contour_yaplot(reflected.contour_flakes(10)), end="")
                print("@ 3")
                print(shifted.contour_yaplot(shifted.contour_flakes(10)))

    sys.exit(0)
            
    #7-1 translate in z/2 and reflect in x
    reflected = contour.PBCGrid()
    reflected.grid = g.grid[::-1, :,: ]
    for sx in range(nx):
        shifted = contour.PBCGrid()
        shifted.grid =  np.roll(np.roll(g.grid, sx, axis=0), nz//2, axis=2)
        score = np.sum(shifted.grid*reflected.grid) /maxscore
        if score > 0.7:
            cx = (nx-1-sx)/2.0
            logger.info("7glidez/2:x {0} {1}".format(cx, score))
            if yaplot:
                #direct action
                print("@ 2\nt 0 0 1.05 7glidez/2:x {0} {1}".format(cx, score))
                print(yap_xplane_at((sx+cx)/nx))
                print("@ 0")
                flakes = reflected.contour_flakes(10)
                print(reflected.contour_yaplot(flakes), end="")
                print("@ 4")
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([sx, 0, nz//2])
                print(g.contour_yaplot(flakes))
                #shifted expression
                print("@ 2\nt 0 0 1.05 7glidez/2:x {0} {1}".format(cx, score))
                print("@ 0")
                print(reflected.contour_yaplot(reflected.contour_flakes(10)), end="")
                print("@ 3")
                print(shifted.contour_yaplot(shifted.contour_flakes(10)))

    sys.exit(0)
    #4 symmetric centers
    #このreflectedは，全反転したので，原点の格子点が[-1,-1,-1]に動いている．
    reflected = contour.PBCGrid()
    reflected.grid = g.grid[::-1, ::-1, ::-1]
    for sx in range(-1,nx+1):
        for sy in range(-1,ny+1):
            for sz in range(-1,nz+1):
                shifted = contour.PBCGrid()
                shifted.grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2)
                score = np.sum(shifted.grid*reflected.grid) /maxscore
                if score > 0.7:
                    #不動点が回転中心，のはず
                    cx,cy,cz = (nx-1-sx)/2.0, (ny-1-sy)/2.0, (nz-1-sz)/2
                    logger.info("4center {0} {1} {2} {3}".format(cx,cy,cz,score))
                    if yaplot:
                        #direct action
                        print("@ 2\nt 0 0 1.05 4center {0} {1} {2} {3}".format(cx,cy,cz, score))
                        print("r 0.01\nc {0} {1} {2}".format((sx+cx)/nx,(sy+cy)/ny,(sz+cz)/nz))
                        print("@ 0")
                        flakes = reflected.contour_flakes(10)
                        print(reflected.contour_yaplot(flakes), end="")
                        print("@ 4")
                        flakes = g.contour_flakes(10)
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        print(g.contour_yaplot(flakes))
                        #shifted expression
                        print("@ 2\nt 0 0 1.05 4center {0} {1} {2} {3}".format(cx,cy,cz, score))
                        print("@ 0")
                        print(reflected.contour_yaplot(reflected.contour_flakes(10)), end="")
                        print("@ 3")
                        print(shifted.contour_yaplot(shifted.contour_flakes(10)))


                    

    #6 screw axis 90 deg
    #90度回転したので，原点は[-1,0,0]に動いた．
    rotated = contour.PBCGrid()
    rotated.grid = np.rot90(g.grid, 3)
    for sx in range(nx):
        for sy in range(ny):
            for sz in (nz//4, -nz//4):
                shifted = contour.PBCGrid()
                shifted.grid =  np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2)
                score = np.sum(shifted.grid*rotated.grid) /maxscore
                if score > 0.7:
                    #この場合，回転とshiftの結果の不動点が回転中心なのだが，それはどこか．
                    #It seems to be wrong.
                    cx = (nx-1-sx-sy)/2.0 #Right
                    cy = (ny-1+sx-sy)/2.0 #Right
                    logger.info("6screw90 {0} {1} {2} {3}".format(cx, cy, sz, score))
                    if yaplot:
                        #direct action
                        print("@ 2\nt 0 0 1.05 6screw90 {0} {1} {2} {3} {4} {5}".format(cx, cy, sz, score, sx, sy))
                        print("l {0} {1} {2} {3} {4} {5}".format((sx+cx)/nx,(sy+cy)/ny,0,(sx+cx)/nx,(sy+cy)/ny,1))
                        print("@ 0")
                        flakes = rotated.contour_flakes(10)
                        print(rotated.contour_yaplot(flakes), end="")
                        print("@ 4")
                        flakes = g.contour_flakes(10)
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        print(g.contour_yaplot(flakes))
                        #shifted expression
                        print("@ 2\nt 0 0 1.05 6screw90 {0} {1} {2} {3}".format(cx, cy, sz, score))
                        print("@ 0")
                        print(rotated.contour_yaplot(rotated.contour_flakes(10)), end="")
                        print("@ 3")
                        print(shifted.contour_yaplot(shifted.contour_flakes(10)))

    sys.exit(0)

    #1 translation
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = contour.PBCGrid()
                shifted.grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2)
                score = np.sum(shifted.grid*g.grid) / maxscore
                if score > 0.7:
                    logger.info(("trans {0} {1} {2} {3}".format(sx,sy,sz, score)))
                    if yaplot:
                        #direct action
                        print("@ 2\nt 0 0 1.05 trans {0} {1} {2} {3}".format(sx,sy,sz, score))
                        print("@ 0")
                        flakes = g.contour_flakes(10)
                        print(g.contour_yaplot(flakes), end="")
                        print("@ 4")
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        print(g.contour_yaplot(flakes))
                        #shifted expression
                        print("t 0 0 1.05 trans {0} {1} {2} {3}".format(sx,sy,sz, score))
                        print("@ 0")
                        flakes = g.contour_flakes(10)
                        print(g.contour_yaplot(flakes), end="")
                        print("@ 3")
                        print(shifted.contour_yaplot(shifted.contour_flakes(10)))




    #7-11 translate in x/2 and reflect in y
    reflected = g.grid[:, ::-1,: ]
    for sy in range(ny):
        shifted =  np.roll(np.roll(g.grid, sy, axis=1), nx/2, axis=0)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cy = (ny-1-sy)/2.0
            logger.info("7glidex/2:y {0} {1}".format(cy, score))
                    
    #7-12 translate in x/2 and reflect in z
    reflected = g.grid[:, :,::-1 ]
    for sz in range(nz):
        shifted =  np.roll(np.roll(g.grid, sz, axis=2), nx/2, axis=0)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cz = (nz-1-sz)/2.0
            logger.info("7glidex/2:z {0} {1}".format(cz, score))
                    
    #7-21 translate in y/2 and reflect in z
    reflected = g.grid[:, :,::-1 ]
    for sz in range(nz):
        shifted =  np.roll(np.roll(g.grid, sz, axis=2), ny/2, axis=1)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cz = (nz-1-sz)/2.0
            logger.info("7glidey/2:z {0} {1}".format(cz, score))
                    
    #7-22 translate in y/2 and reflect in x
    reflected = g.grid[::-1, :,: ]
    for sx in range(nx):
        shifted =  np.roll(np.roll(g.grid, sx, axis=0), ny/2, axis=1)
        score = np.sum(shifted*reflected) /maxscore
        if score > 0.7:
            cx = (nx-1-sx)/2.0
            logger.info("7glidey/2:x {0} {1}".format(cx, score))
                    
    #3-3 rot z
    rotated = g.grid[::-1, ::-1, 0]
    for sx in range(nx):
        for sy in range(ny):
            shifted =  np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1)
            score = np.sum(shifted*rotated) /maxscore
            if score > 0.3:
                #nx-1-x=x+sx
                logger.info("rotz {0} {1} {2}".format((nx-1-sx)/2.0, (ny-1-sy)/2.0, score))

    #2 mirror
    #2-1 mirror x
    #原点は[-1,0,0]に移動した
    mirrored = g.grid[::-1, :, :]
    for s in range(nx+1):
        shifted = np.roll(g.grid, s, axis=0)
        score = np.sum(shifted*mirrored) / maxscore
        if score > 0.7:
            #nx-1-x=x+s
            logger.info("refx {0} {1}".format((nx-1-s)/2.0, score))
            #周期境界なので実際には不動点は2倍ある．

    #2-2 mirror y
    #原点は[-1,0,0]に移動した
    mirrored = g.grid[:, ::-1, :]
    for s in range(ny+1):
        shifted = np.roll(g.grid, s, axis=1)
        score = np.sum(shifted*mirrored) / maxscore
        if score > 0.4:
            #ny-1-y=y+s
            logger.info("refy {0} {1}".format((ny-1-s)/2.0, score))
            #周期境界なので実際には不動点は2倍ある．



    
    #5 rotary reflection 90 deg
    #90度回転し，z方向に反転したので，原点は[-1,0,-1]に動いた．
    rotated = np.rot90(g.grid[:, :, ::-1])
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted =  np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2)
                #rotated = np.roll(np.roll(np.rot90(shifted, k=1)[:, :, ::-1], 1, axis=0), 1, axis=2)
                #logger.info(shifted[0,0,0])
                #logger.info(rotated[0,0,0])
                score = np.sum(shifted*rotated) /maxscore
                if score > 0.7:
                    #この場合，回転とshiftの結果の不動点が回転中心なのだが，それはどこか．
                    cx = (nx-1-sx+sy)/2.0
                    cy = (ny-1-sx-sy)/2.0
                    #nz-1-z = z+sz; (nz-1-sz)/2 = z;
                    cz = (nz-1-sz) / 2.0
                    logger.info("rotrefz {0} {1} {2} {3}".format(cx, cy, cz, score))


    #2-4 xとyの交換=  x=yでの鏡映
    #原点は動かない．
    mirrored = np.transpose(g.grid, (1,0,2))
    for s in range(nx):
        shifted = np.roll(np.roll(g.grid, s, axis=0), -s, axis=1)
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.7:
            logger.info("refxy {0} {1}".format(nx-s/2.0, score))





    
    #2-2 y
    for s in range(ny):
        shifted = np.roll(g.grid, s, axis=1)
        mirrored = shifted[:, ::-1, :]
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            logger.info("refy {0} {1}".format(s, score))
    
    #2-3 z
    for s in range(nz):
        shifted = np.roll(g.grid, s, axis=2)
        mirrored = shifted[:, :, ::-1]
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            logger.info("refz {0} {1}".format(s, score))


    #2-5 x=-y
    mirrored = np.transpose(g.grid[::-1,:,:], (1,0,2))
    for s in range(nx):
        shifted = np.roll(np.roll(g.grid[::-1,:,:], s, axis=0), -s, axis=1)
        score = np.sum(shifted*mirrored) /maxscore
        if score > 0.3:
            logger.info("ref-xy {0} {1}".format(s, score))

    #3 rotation
    #3-1 x
    rotated = g.grid[0, ::-1, ::-1]
    for sy in range(ny):
        for sz in range(nz):
            shifted =  np.roll(np.roll(g.grid, sy, axis=1), sz, axis=2)
            score = np.sum(shifted*rotated) /maxscore
            if score > 0.3:
                logger.info("rotx {0} {1} {2}".format(sy, sz, score))


    
main()


    
