#include <stdio.h>
#include "cont3.h"

float 
  *Grid;
int gx,gy,gz;

void GridDone()
{
  //printf("%x %s\n", Grid, "Grid");
  free(Grid);
}


float
  grid(int x,int y,int z)
{
    return Grid[(x*gy+y)*gz+z];
}

void
  GridInitialize(int ix,int iy,int iz)
{
    int i,j,k;
    float *g;
    
    gx = ix;
    gy = iy;
    gz = iz;
    g= Grid = (float *)malloc(sizeof(float)*gx*gy*gz);
    for(i=0;i<ix;i++)
      for(j=0;j<iy;j++)
	for(k=0;k<iz;k++)
          {
              scanf("%f",g++);
/*              fprintf(stderr,"%d %d %d %f\n",i,j,k,grid(i,j,k));*/
          }
}

