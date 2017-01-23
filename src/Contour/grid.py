#!/usr/bin/env python

class PBCGrid():
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

    def contour_surface(self, value):
        s = [] #array of something.
        for x in range(self.grid.shape[0]):
            xs, xe = x, x+2
            if xe == 
            for y in range(self.grid.shape[1]-1):
                for z in range(self.grid.shape[2]-1):
                    s += contour_surface_in_a_cube(self.grid[x:x+2,y:y+2,z:z+2], value)
                    s += contour_surface_in_a_cube(self.grid[x:x+2,y:y+2,z:z+2], value)
                
        
        
