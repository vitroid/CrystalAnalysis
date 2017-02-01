#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Find the symmetry in the grid data.
import numpy as np
import sys
import logging
import grid



def yap_xplane_at(x):
    return "p 4 {0} 0 0 {0} 1 0 {0} 1 1 {0} 0 1\n".format(x)


def yap_yplane_at(y):
    return "p 4 0 {0} 0 0 {0} 1 1 {0} 1 1 {0} 0\n".format(y)

def yap_zplane_at(z):
    return "p 4 0 0 {0} 0 1 {0} 1 1 {0} 1 0 {0}\n".format(z)

def yap_line(x,y,z,a,b,c):
    return "l {0} {1} {2} {3} {4} {5} \n".format(x,y,z,a,b,c)

def yap_circle(x,y,z):
    return "c {0} {1} {2}\n".format(x,y,z)

def yap_palette(p):
    return "@ {0}\n".format(p)

def yap_radius(r):
    return "r {0}\n".format(r)

def yap_text(x,y,z,msg):
    return "t {0} {1} {2} {3}\n".format(x,y,z,msg)

def yap_overlay(g1,g2,msg,palette1=0,palette2=3):
    s = yap_text(0,0,1.05,msg)
    s += yap_palette(palette1)
    s += g1.contour_yaplot(g1.contour_flakes(10))
    s += yap_palette(palette2)
    s += g2.contour_yaplot(g2.contour_flakes(10))
    return s


def mirror_x(grid):
    return np.roll(grid[::-1, :, :], 1, axis=0)

def mirror_y(grid):
    return np.roll(grid[:, ::-1, :], 1, axis=1)

def mirror_z(grid):
    return np.roll(grid[:, :, ::-1], 1, axis=2)



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
                g = grid.Contour(file=file)
                nx,ny,nz = g.grid.shape

    maxscore = np.sum(g.grid*g.grid)
    #g.grid =  np.roll(g.grid, -4, axis=0)

    #原点にずらしてから，原点に関して対称操作を行うほうが直感的にはわかりやすいが，
    #対称操作を行ってから原点をずらす方が精密な照合ができる．
    #後者を行う場合には，表現方法を工夫する必要がある．
        
    #2 mirror
    #2-1 mirror x
    #原点は[-1,0,0]に移動した
    rotref = grid.Contour(grid = g.grid[::-1, :, :])
    for s in range(nx+1):
        shifted = grid.Contour(grid = np.roll(g.grid, s, axis=0))
        score = np.sum(shifted.grid*rotref.grid) / maxscore
        if score > 0.6:
            #nx-1-x=x+s
            msg = "a-mirror {0} {1}".format((nx-1-s)/2.0, score)
            logger.info(msg)
            #周期境界なので実際には不動点は2倍ある．

    #2-2 mirror y
    #原点は[-1,0,0]に移動した
    rotref = grid.Contour(grid = g.grid[:, ::-1, :])
    for s in range(ny+1):
        shifted = grid.Contour(grid = np.roll(g.grid, s, axis=1))
        score = np.sum(shifted.grid*rotref.grid) / maxscore
        if score > 0.6:
            #ny-1-y=y+s
            msg = "b-mirror {0} {1}".format((ny-1-s)/2.0, score)
            logger.info(msg)
            #周期境界なので実際には不動点は2倍ある．
            
    #3 rotation
    #3-1 x
    rotref = grid.Contour( grid = g.grid[:, ::-1, ::-1] )
    for sy in range(ny):
        for sz in range(nz):
            shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sy, axis=1), sz, axis=2))
            score = np.sum(shifted.grid*rotref.grid) /maxscore
            if score > 0.6:
                cz = (nz-1-sz)/2.0
                cy = (ny-1-sy)/2.0
                msg = "a-rot180 {0} {1} {2}".format(cy, cz, score)
                logger.info(msg)
                if yaplot:
                    #direct action
                    s = yap_palette(2)
                    s += yap_text(0,0,1.05,msg)
                    s += yap_line(0,(cy+sy)/ny,(cz+sz)/nz,1,(cy+sy)/ny,(cz+sz)/nz)
                    s += yap_palette(0)
                    s += rotref.contour_yaplot(rotref.contour_flakes(10))
                    s += yap_palette(4)
                    flakes = g.contour_flakes(10)
                    for i in range(len(flakes)):
                        flakes[i] += np.array([0,sy,sz])
                    s += g.contour_yaplot(flakes)
                    print(s)
                    #shifted expression
                    print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))

    #3-2 y
    rotref = grid.Contour( grid = g.grid[::-1, :, ::-1] )
    for sx in range(nx):
        for sz in range(nz):
            shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sx, axis=0), sz, axis=2))
            score = np.sum(shifted.grid*rotref.grid) /maxscore
            if score > 0.6:
                cz = (nz-1-sz)/2.0
                cx = (nx-1-sx)/2.0
                msg = "b-rot180 {0} {1} {2}".format(cx, cz, score)
                logger.info(msg)
                if yaplot:
                    #direct action
                    s = yap_palette(2)
                    s += yap_text(0,0,1.05,msg)
                    s += yap_line((cx+sx)/nx,0,(cz+sz)/nz,(cx+sx)/nx,1,(cz+sz)/nz)
                    s += yap_palette(0)
                    s += rotref.contour_yaplot(rotref.contour_flakes(10))
                    s += yap_palette(4)
                    flakes = g.contour_flakes(10)
                    for i in range(len(flakes)):
                        flakes[i] += np.array([sx,0,sz])
                    s += g.contour_yaplot(flakes)
                    print(s)
                    #shifted expression
                    print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))
                    
    #3-3 rot z
    rotref = grid.Contour(grid = g.grid[::-1, ::-1, :])
    for sx in range(nx+1):
        for sy in range(ny+1):
            shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1))
            score = np.sum(shifted.grid*rotref.grid) /maxscore
            if score > 0.6:
                #nx-1-x=x+sx
                cx = (nx-1-sx)/2.0
                cy = (ny-1-sy)/2.0
                msg = "c-rot180 {0} {1} {2}".format(cx,cy, score)
                logger.info(msg)
                if yaplot:
                    #direct action
                    s = yap_palette(2)
                    s += yap_text(0,0,1.05,msg)
                    s += yap_line((cx+sx)/nx,(cy+sy)/ny,0,(cx+sx)/nx,(cy+sy)/ny,1)
                    s += yap_palette(0)
                    s += rotref.contour_yaplot(rotref.contour_flakes(10))
                    s += yap_palette(4)
                    flakes = g.contour_flakes(10)
                    for i in range(len(flakes)):
                        flakes[i] += np.array([sx,sy,0])
                    s += g.contour_yaplot(flakes)
                    print(s)
                    #shifted expression
                    print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))

    #7 glide reflection
    #There many possible ways....
    #7-31 translate in (x+y)/2 and reflect in z
    rotref = grid.Contour(grid = g.grid[:, :, ::-1 ])
    for sz in range(nz):
        shifted = grid.Contour(grid =  np.roll(np.roll(np.roll(g.grid, sz, axis=2), ny//2, axis=1), nx//2, axis=0))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cz = (nz-1-sz)/2.0
            msg = "n-glide_ab|c {0} {1}".format(cz, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_zplane_at((sz+cz)/nz)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([nx//2, ny//2, sz])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))

                
    #7-11 translate in x/2 and reflect in y
    rotref = grid.Contour(grid = g.grid[:, ::-1,: ])
    for sy in range(ny):
        shifted = grid.Contour(grid = np.roll(np.roll(g.grid, sy, axis=1), nx//2, axis=0))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cy = (ny-1-sy)/2.0
            msg = "a-glide|b {0} {1}".format(cy, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_yplane_at((sy+cy)/ny)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([nx//2, sy, 0])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))
                    
    #7-12 translate in x/2 and reflect in z
    rotref = grid.Contour(grid = g.grid[:, :,::-1 ])
    for sz in range(nz):
        shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sz, axis=2), nx//2, axis=0))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cz = (nz-1-sz)/2.0
            msg = "a-glide|c {0} {1}".format(cz, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_zplane_at((sz+cz)/nz)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([nx//2, 0, sz])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))
                    
    #7-21 translate in y/2 and reflect in z
    rotref = grid.Contour(grid = g.grid[:, :,::-1 ])
    for sz in range(nz):
        shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sz, axis=2), ny//2, axis=1))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cz = (nz-1-sz)/2.0
            msg = "b-glide|c {0} {1}".format(cz, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_zplane_at((sz+cz)/nz)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([0, ny//2, sz])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))
                    
    #7-22 translate in y/2 and reflect in x
    rotref = grid.Contour(grid = g.grid[::-1, :,: ])
    for sx in range(nx):
        shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sx, axis=0), ny//2, axis=1))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cx = (nx-1-sx)/2.0
            msg = "b-glide|a {0} {1}".format(cx, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_xplane_at((sx+cx)/nx)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([sx, ny//2, 0])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))
                    


    #7-2 translate in z/2 and reflect in y
    rotref = grid.Contour(grid = g.grid[:, ::-1,: ])
    for sy in range(ny):
        shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sy, axis=1), nz//2, axis=2))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cy = (ny-1-sy)/2.0
            msg = "c-glide|b {0} {1}".format(cy, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_yplane_at((sy+cy)/ny)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([0, sy, nz//2])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))

    #7-1 translate in z/2 and reflect in x
    rotref = grid.Contour(grid = g.grid[::-1, :,: ])
    for sx in range(nx):
        shifted = grid.Contour(grid =  np.roll(np.roll(g.grid, sx, axis=0), nz//2, axis=2))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            cx = (nx-1-sx)/2.0
            msg = "c-glide|a {0} {1}".format(cx, score)
            logger.info(msg)
            if yaplot:
                #direct action
                s = yap_palette(2)
                s += yap_text(0,0,1.05,msg)
                s += yap_xplane_at((sx+cx)/nx)
                s += yap_palette(0)
                s += rotref.contour_yaplot(rotref.contour_flakes(10))
                s += yap_palette(4)
                flakes = g.contour_flakes(10)
                for i in range(len(flakes)):
                    flakes[i] += np.array([sx, 0, nz//2])
                s += g.contour_yaplot(flakes)
                print(s)
                #shifted expression
                print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))


    #4 symmetric centers
    #このrotrefは，全反転したので，原点の格子点が[-1,-1,-1]に動いている．
    rotref = grid.Contour(grid = g.grid[::-1, ::-1, ::-1])
    for sx in range(-1,nx+1):
        for sy in range(-1,ny+1):
            for sz in range(-1,nz+1):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.6:
                    #不動点が回転中心，のはず
                    cx,cy,cz = (nx-1-sx)/2.0, (ny-1-sy)/2.0, (nz-1-sz)/2
                    msg = "center {0} {1} {2} {3}".format(cx,cy,cz,score)
                    logger.info(msg)
                    if yaplot:
                        #direct action
                        s = yap_palette(2)
                        s += yap_text(0,0,1.05,msg)
                        s += yap_radius(0.01)
                        s += yap_circle((sx+cx)/nx,(sy+cy)/ny,(sz+cz)/nz)
                        s += yap_palette(0)
                        s += rotref.contour_yaplot(rotref.contour_flakes(10))
                        s += yap_palette(4)
                        flakes = g.contour_flakes(10)
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        s += g.contour_yaplot(flakes)
                        print(s)
                        #shifted expression
                        print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))


                    

    #6 screw axis 90 deg
    #90度回転したので，原点は[-1,0,0]に動いた．
    rotref = grid.Contour(grid = np.rot90(g.grid, 3))
    for sx in range(nx):
        for sy in range(ny):
            for iz in (1,2,3):
                sz = nz*iz//4
                shifted = grid.Contour(grid =  np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.6:
                    #この場合，回転とshiftの結果の不動点が回転中心なのだが，それはどこか．
                    #It seems to be wrong.
                    cx = (nx-1-sx-sy)/2.0 #Right
                    cy = (ny-1+sx-sy)/2.0 #Right
                    msg = "c_screw4_{2} {0} {1} {3}".format(cx, cy, iz, score)
                    logger.info(msg)
                    if yaplot:
                        #direct action
                        s = yap_palette(2)
                        s += yap_text(0,0,1.05,msg)
                        s += yap_line((sx+cx)/nx,(sy+cy)/ny,0,(sx+cx)/nx,(sy+cy)/ny,1)
                        s += yap_palette(0)
                        s += rotref.contour_yaplot(rotref.contour_flakes(10))
                        s += yap_palette(4)
                        flakes = g.contour_flakes(10)
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        s += g.contour_yaplot(flakes)
                        print(s)
                        #shifted expression
                        print(yap_overlay(rotref, shifted, msg, palette1=0, palette2=3))




                        
    #1 translation
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                score = np.sum(shifted.grid*g.grid) / maxscore
                if score > 0.6:
                    msg = "trans {0} {1} {2} {3}".format(sx,sy,sz, score)
                    logger.info(msg)
                    if yaplot:
                        #direct action
                        s = yap_palette(2)
                        s += yap_text(0,0,1.05,msg)
                        s += yap_palette(0)
                        s += g.contour_yaplot(g.contour_flakes(10))
                        s += yap_palette(4)
                        flakes = g.contour_flakes(10)
                        for i in range(len(flakes)):
                            flakes[i] += np.array([sx, sy, sz])
                        s += g.contour_yaplot(flakes)
                        print(s)
                        #shifted expression
                        print(yap_overlay(g, shifted, msg, palette1=0, palette2=3))



    #8-1 diagonal rotation 120 degree
    #原点は動かない．
    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                #rotation after shift (because it is too confusing for me)
                rotref = grid.Contour(grid = np.transpose(shifted.grid, (1,2,0)))
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.5:
                    msg = "diagrot {0} {1} {2} {3}".format(sx,sy,sz, score)
                    logger.info(msg)

    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                #rotation after shift (because it is too confusing for me)
                r = mirror_x(shifted.grid)
                r = np.transpose(r, (1,2,0))
                r = mirror_x(r)
                rotref = grid.Contour(grid = r)
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.5:
                    msg = "diagrot {0} {1} {2} {3}".format(sx,sy,sz, score)
                    logger.info(msg)

    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                #rotation after shift (because it is too confusing for me)
                r = mirror_y(shifted.grid)
                r = np.transpose(r, (1,2,0))
                r = mirror_y(r)
                rotref = grid.Contour(grid = r)
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.5:
                    msg = "diagrot {0} {1} {2} {3}".format(sx,sy,sz, score)
                    logger.info(msg)

    for sx in range(nx):
        for sy in range(ny):
            for sz in range(nz):
                shifted = grid.Contour(grid = np.roll(np.roll(np.roll(g.grid, sx, axis=0), sy, axis=1), sz, axis=2))
                #rotation after shift (because it is too confusing for me)
                r = mirror_z(shifted.grid)
                r = np.transpose(r, (1,2,0))
                r = mirror_z(r)
                rotref = grid.Contour(grid = r)
                score = np.sum(shifted.grid*rotref.grid) /maxscore
                if score > 0.5:
                    msg = "diagrot {0} {1} {2} {3}".format(sx,sy,sz, score)
                    logger.info(msg)

    sys.exit(0)



    


    #2-4 xとyの交換=  x=yでの鏡映
    #原点は動かない．
    rotref = grid.Contour(grid = np.transpose(g.grid, (1,0,2)))
    for s in range(nx):
        shifted = grid.Contour(grid = np.roll(np.roll(g.grid, s, axis=0), -s, axis=1))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.6:
            msg = "ab-mirror {0} {1}".format(nx-s/2.0, score)
            logger.info(msg)




    
    #2-3 z
    for s in range(nz):
        shifted = grid.Contour(grid = np.roll(g.grid, s, axis=2))
        rotref = grid.Contour(grid = shifted[:, :, ::-1])
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.3:
            msg = "c-mirror {0} {1}".format(s, score)
            logger.info(msg)


    #2-5 x=-y
    rotref = grid.Contour(grid = np.transpose(g.grid[::-1,:,:], (1,0,2)))
    for s in range(nx):
        shifted = grid.Contour(grid = np.roll(np.roll(g.grid[::-1,:,:], s, axis=0), -s, axis=1))
        score = np.sum(shifted.grid*rotref.grid) /maxscore
        if score > 0.3:
            msg = "a-b-mirror {0} {1}".format(s, score)
            logger.info(msg)



    
main()


    
