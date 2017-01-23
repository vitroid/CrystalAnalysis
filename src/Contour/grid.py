#!/usr/bin/env python3

import numpy as np





class PBCGrid():
    #node ID: 0..7
    #edge is identified by two 
    edges = set()
    for x in range(0,8,4):
        for y in range(0,4,2):
            edges.add((x+y+0, x+y+1))
    for x in range(0,8,4):
        for z in range(0,2,1):
            edges.add((x+0+z, x+2+z))
    for y in range(0,4,2):
        for z in range(0,2,1):
            edges.add((0+y+z, 4+y+z))

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

    
    def __init__(self, ngrid):
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
    
    def double(self):
        """
        double the lattice by linear interpolation
        """
        newgrid = np.zeros(2*self.grid.shape)
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                for z in range(self.grid.shape[2]):
                    x2 = x*2
                    y2 = y*2
                    z2 = z*2
                    newgrid[x2,y2,z2] = self.grid[x,y,z]
                    newgrid[x2-1,y2,z2] = (self.grid[x,y,z]+self.grid[x-1,y,z])/2.0
                    newgrid[x2,y2-1,z2] = (self.grid[x,y,z]+self.grid[x,y-1,z])/2.0
                    newgrid[x2,y2,z2-1] = (self.grid[x,y,z]+self.grid[x,y,z-1])/2.0
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                for z in range(self.grid.shape[2]):
                    x2 = x*2
                    y2 = y*2
                    z2 = z*2
                    newgrid[x2-1,y2-1,z2] = (newgrid[x2-1,y2-2,z2]+newgrid[x2-1,y2,z2])/2.0
                    newgrid[x2-1,y2,z2-1] = (newgrid[x2-1,y2,z2-2]+newgrid[x2-1,y2,z2])/2.0
                    newgrid[x2,y2-1,z2-1] = (newgrid[x2,y2-2,z2-1]+newgrid[x2,y2,z2-1])/2.0
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                for z in range(self.grid.shape[2]):
                    x2 = x*2
                    y2 = y*2
                    z2 = z*2
                    newgrid[x2-1,y2-1,z-1] = (newgrid[x2-1,y2-1,z2-2]+newgrid[x2-1,y2-1,z2])/2.0
        self.grid = newgrid


    def contour_surface_in_a_cube(self, cube, value):
        """
        generates the contour magically
        """
                
                
                                
        
    def contour_surface(self, value):
        s = [] #array of something.
        for x in range(self.grid.shape[0]):
            xra = np.array((x,x+1))%self.grid.shape[0]
            for y in range(self.grid.shape[1]-1):
                yra = np.array((y,y+1))%self.grid.shape[1]
                for z in range(self.grid.shape[2]-1):
                    zra = np.array((z,z+1))%self.grid.shape[2]
                    s += contour_surface_in_a_cube(self.grid[xra,yra,zra].reshape((8,)), value)


def test():
    g = PBCGrid((5,5,5))
    ret = g.contour_surface_in_a_cube([1.,0.,0.,1.,0.,0.,0.,1.], 0.3)
    print(ret)

    
        
        
test()
