#include <ctype.h>
#include	<stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <unistd.h>
#include "cont3.h"

/*user define*/
Face *facelist;/*dummy first object of chain list*/


void usage(char *cmd)
{
    fprintf(stderr,"usage: %s [-x][-y][-z][-s][-l][-Y][-c r,g,b][-Z x] threshold < file.grid > file.hull\n",cmd);
    fprintf(stderr,"\t-x:Draw X cross section faces\n");
    fprintf(stderr,"\t-y:Draw Y cross section faces\n");
    fprintf(stderr,"\t-z:Draw Z cross section faces\n");
    fprintf(stderr,"\t-s:Do not draw surface\n");
    fprintf(stderr,"\t-l:Draw cross section if below the threshold\n");
    fprintf(stderr,"\t-Y:Output in yaplot format\n");
    fprintf(stderr,"\t-c:Determine color (r,g,b: 0..255)\n");
    fprintf(stderr,"\t-Z x:zoom ratio\n");
    exit(1);
}


int
  main(int argc,char *argv[])
{
    Face *face;
    int red=255,green=255,blue=255;
    char s[255];
    int ix,iy,iz;
    float threshold;
    
    extern char *optarg;
    extern int optind, optopt;
    int mode=SURFACE;
    int err=0;
    char c;
    double bx,by,bz;
    int yaplot=0;
    float zoom=1;
    
    while ((c = getopt(argc, argv, ":c:Z:xyzlsY")) != -1)
      switch (c) {
        case 'c':
          sscanf(optarg,"%d,%d,%d",&red,&green,&blue);
          break;
        case 'x':
          mode|=CROSSX;
          break;
        case 'y':
          mode|=CROSSY;
          break;
        case 'z':
          mode|=CROSSZ;
          break;
        case 'Z':
          sscanf(optarg,"%f",&zoom);
          break;
        case 'l':
          mode|=FILLBELOW;
          break;
        case 's':
          mode^=SURFACE;
          break;
      case 'Y':
	yaplot++;
	break;
        case ':':
          err++;
          break;
        case '?':
          err++;
          break;
      }
    if((optind+1)!=argc)err++;
    if(err)usage(argv[0]);
    threshold=atof(argv[optind]);
    bx=by=bz=1;
    zoom *= 0.5;

/*平成１１年１月１２日(火)変更。ヘッダ@GRIDをさがす。*/    
    while(NULL!=fgets(s,sizeof(s),stdin))
      {
	if(strncmp(s,"@BOX3",5)==0){
	  fgets(s,sizeof(s),stdin);
	  sscanf(s,"%lf %lf %lf\n",&bx,&by,&bz);
	}
	if(strncmp(s,"@GRID",5)==0)
	  {
	    fgets(s,sizeof(s),stdin);
	    sscanf(s,"%d %d %d\n",&ix,&iy,&iz);
	    /*fprintf(stderr,"%d %d %d\n",ix,iy,iz);*/
	    GridInitialize(ix,iy,iz);
	    MakeList(mode,threshold);
	    if(yaplot){
	      for(face=facelist;face!=NULL;face=face->next){
		Point *q;
		int i;
		/*
		printf("p %d ",face->nvertex);
		for(i=0;i<face->nvertex;i++){
		  float x,y,z;
		  x = face->point[i]->org.coord[0];
		  y = face->point[i]->org.coord[1];
		  z = face->point[i]->org.coord[2];
		  x -= ix/2;
		  y -= iy/2;
		  z -= iz/2;
		  x *= bx*zoom/(ix/2);
		  y *= by*zoom/(iy/2);
		  z *= bz*zoom/(iz/2);
		  printf("%f %f %f ",x,y,z);
		}
		putchar('\n');
		*/
		for(i=0;i<face->nvertex;i++){
		  float x,y,z;
		  x = face->point[i]->org.coord[0];
		  y = face->point[i]->org.coord[1];
		  z = face->point[i]->org.coord[2];
		  x -= ix/2;
		  y -= iy/2;
		  z -= iz/2;
		  x *= bx*zoom/(ix/2);
		  y *= by*zoom/(iy/2);
		  z *= bz*zoom/(iz/2);
		  float xj,yj,zj;
		  int j;
		  j = i+1;
		  if ( j == face->nvertex )j=0;
		  xj = face->point[j]->org.coord[0];
		  yj = face->point[j]->org.coord[1];
		  zj = face->point[j]->org.coord[2];
		  xj -= ix/2;
		  yj -= iy/2;
		  zj -= iz/2;
		  xj *= bx*zoom/(ix/2);
		  yj *= by*zoom/(iy/2);
		  zj *= bz*zoom/(iz/2);
		  printf("l %f %f %f %f %f %f\n",x,y,z,xj,yj,zj);
		}
	      }
	      putchar('\n');
	    }else{
	      for(face=facelist;face!=NULL;face=face->next)
		{
		  Point *q;
		  int i;
		  printf("%d %d %d #NP:%d\n\n",red,green,blue,face->nvertex);
		  for(i=0;i<face->nvertex;i++)
		    {
		      float x,y,z,nx,ny,nz;
		      nx = face->point[i]->norm.coord[0];
		      ny = face->point[i]->norm.coord[1];
		      nz = face->point[i]->norm.coord[2];
		      x = face->point[i]->org.coord[0];
		      y = face->point[i]->org.coord[1];
		      z = face->point[i]->org.coord[2];
		      x -= ix/2;
		      y -= iy/2;
		      z -= iz/2;
		      x *= bx*zoom/(ix/2);
		      y *= by*zoom/(iy/2);
		      z *= bz*zoom/(iz/2);
		      
		      printf("%f %f %f %f %f %f\n",x,y,z,nx,ny,nz);
		    }
		  putchar('\n');
		}
	    }
	    FreeList();
	    GridDone();
	  }
      }
    exit(0);
}
