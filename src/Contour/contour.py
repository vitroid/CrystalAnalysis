#!/usr/bin/env python3

import numpy as np
import sys




class PBCGrid():
    #vertex ID: x*4+y*2+z for x,y,z in (0,1)
    vertices = np.array([(0.0,0.0,0.0),(0.0,0.0,1.0),(0.0,1.0,0.0),(0.0,1.0,1.0),
                         (1.0,0.0,0.0),(1.0,0.0,1.0),(1.0,1.0,0.0),(1.0,1.0,1.0)])
    
    edges = [(0,4), (0,2), (0,1),
             (1,5), (1,3), (2,3),
             (3,7), (5,7), (6,7),
             (2,6), (4,6), (4,5)]

    neibor = [[None,      [11, 3, 2], [1, 9,10]],
              [[2, 4, 5], None,       [9,10, 0]],
              [[4, 5, 1], [0,11, 3],  None],
              [None,      [2, 0,11],  [7, 6, 4]],
              [[5, 1, 2], None,       [3, 7, 6]],
              [[1, 2, 4], [6, 8, 9],  None],
              [None,      [8, 9, 5],  [4, 3, 7]],
              [[11,10, 8], None,      [6, 4, 3]],
              [[7,11,10], [9, 5, 6],  None],
              [None,      [5, 6, 8],  [10, 0, 1]],
              [[8, 7,11], None,       [0, 1, 9]],
              [[10, 8, 7],[3, 2, 0],  None]]

    
    def __init__(self, ngrid=None, file=None):
        if file is not None:
            self.load(file)
        elif ngrid is not None:
            self.grid = np.zeros(ngrid)
        
    def load(self, file):
        line = file.readline()
        nx,ny,nz = [int(x) for x in line.split()]
        self.grid = np.zeros((nx,ny,nz))
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    value = float(file.readline())
                    self.grid[x,y,z] = value

    def serialize(self):
        s = "@GRID\n"
        s += "{0} {1} {2}\n".format(*self.grid.shape)
        for x in self.grid.reshape((np.product(self.grid.shape),)):
            s+= "{0}\n".format(x)
        return s
    
    def doublex(self, grid):
        """
        double the lattice by linear interpolation
        """
        shape = list(grid.shape)
        shape[0]*=2
        newgrid = np.zeros(shape)
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                for z in range(grid.shape[2]):
                    x2 = x*2
                    newgrid[x2,y,z] = grid[x,y,z]
                    newgrid[x2-1,y,z] = (grid[x,y,z] + grid[x-1,y,z])/2.0
        return newgrid
    

    def doubley(self, grid):
        """
        double the lattice by linear interpolation
        """
        shape = list(grid.shape)
        shape[1]*=2
        newgrid = np.zeros(shape)
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                for z in range(grid.shape[2]):
                    y2 = y*2
                    newgrid[x,y2,z] = grid[x,y,z]
                    newgrid[x,y2-1,z] = (grid[x,y,z] + grid[x,y-1,z])/2.0
        return newgrid
    

    def doublez(self, grid):
        """
        double the lattice by linear interpolation
        """
        shape = list(grid.shape)
        shape[2]*=2
        newgrid = np.zeros(shape)
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                for z in range(grid.shape[2]):
                    z2 = z*2
                    newgrid[x,y,z2] = grid[x,y,z]
                    newgrid[x,y,z2-1] = (grid[x,y,z] + grid[x,y,z-1])/2.0
        return newgrid
    

    def double(self):
        """
        double the lattice by linear interpolation
        """
        self.grid = self.doublez(self.doubley(self.doublex(self.grid)))
        

    def cube_next(self, fi, edge, eorder):
        for fj in range(3):
            if fj != fi and self.neibor[edge][fj] is not None:
                for nextedge in self.neibor[edge][fj]:
                    if nextedge not in self.emark:
                        self.emark.add(nextedge)
                        if 0 <= self.ep[nextedge] <= 1:
                            neworder = self.cube_next(fj,nextedge, eorder+[edge])
                            return neworder
        return eorder+[edge]

    def cube_contour_edge_order(self):
        eorders = []
        for e in range(12):
            if e not in self.emark:
                self.emark.add(e)
                if 0 <= self.ep[e] <= 1:
                    for fi in range(3):
                        edges = self.neibor[e][fi]
                        if edges is not None:
                            for nextedge in edges:
                                if nextedge not in self.emark:
                                    self.emark.add(nextedge)
                                    if 0 <= self.ep[nextedge] <= 1:
                                        eorders.append(self.cube_next(fi,nextedge, [e,]))
        return eorders
                            
                
    def contour_surface_in_a_cube(self, cube, value):
        """
        generates the contour magically
        """
        self.ep = []
        self.emark = set()
        for k in range(len(self.edges)):
            i,j = self.edges[k]
            if cube[i] == cube[j]:
                if cube[i] == value:
                    p = 0.5
                else:
                    p = -1
            else:
                p = (value - cube[i])/(cube[j] - cube[i])
            self.ep.append(p)
            if not (0 <= p <= 1):
                self.emark.add(k)
                
        edge_orders = self.cube_contour_edge_order()
        #from edge orders to vertex positions
        polys = []
        for edge_order in edge_orders:
            poly = []
            for edge in edge_order:
                i,j = self.edges[edge]
                p = self.ep[edge]
                v = self.vertices[i]*(1-p) + self.vertices[j]*p
                poly.append(v)
            polys.append(poly)
        return polys
                                
        
    def contour_flakes(self, value):
        s = [] #array of something.
        for x in range(self.grid.shape[0]):
            xra = np.array((x,x+1))%self.grid.shape[0]
            for y in range(self.grid.shape[1]-1):
                yra = np.array((y,y+1))%self.grid.shape[1]
                for z in range(self.grid.shape[2]-1):
                    zra = np.array((z,z+1))%self.grid.shape[2]
                    subgrid = np.array([self.grid[xx,yy,zz] for xx in xra for yy in yra for zz in zra])
                    flakes = self.contour_surface_in_a_cube(subgrid, value)
                    for i in range(len(flakes)):
                        flakes[i] += np.array([x, y, z])
                    s += flakes
        return s

    
    def contour_yaplot(self, flakes):
        """
        By default, the lattice is shown in (1x1x1)
        """
        txt = ""
        for poly in flakes:
            txt += "p {0} ".format(len(poly))
            for p in poly:
                x,y,z = p / np.array(self.grid.shape)
                txt += "{0} {1} {2} ".format(x,y,z)
            txt += "\n"
        return txt


def test():
    g = PBCGrid()
    ret = g.contour_surface_in_a_cube([1.,0.,0.,1.,0.,0.,0.,1.], 0.3)
    print(ret)

def test2():
    g = PBCGrid(ngrid=(2,2,2))
    g.grid = np.array([1.,0.,0.,1.,0.,0.,0.,1.]).reshape((2,2,2))
    s = g.contour_flakes(0.3)
    print(s)

def test3():
    file = open("00010-last.unit.avg.grid")
    while True:
        line = file.readline()
        if "@GRID" in line:
            g = PBCGrid(file=file)
            g.double()
            print("@ 3")
            print(g.contour_yaplot(g.contour_flakes(10)), end="")
            g.grid = np.roll(g.grid[::-1, :, :], 1, axis=0)
            print("@ 4")
            print(g.contour_yaplot(g.contour_flakes(10)))
            sys.exit(0)
        
if __name__ == "__main__":
    test()
