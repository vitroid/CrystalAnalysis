#!/usr/bin/env python3

import grid
import sys

def main():
    file = sys.stdin
    thres = float(sys.argv[1])
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        if "@GRID" in line:
            g = grid.Contour(file=file)
            g.double()   #make finer mesh
            print("@ 2") #white
            print(g.contour_yaplot(g.contour_flakes(10)))

        
if __name__ == "__main__":
    main()
