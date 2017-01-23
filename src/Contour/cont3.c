/*$Id: cont3.c,v 1.3 2000/04/21 09:40:15 matto Exp $*/
/*$Log: cont3.c,v $
/*Revision 1.3  2000/04/21 09:40:15  matto
/*Sequential input is OK to contour.
/*
/*Revision 1.2  1999/09/09 04:02:04  matto
/*Modified for non-cubic cell
/*
 *Revision 1.1.1.1  1999/01/12 23:31:15  matto
 *Cont3 is moved from src/misc/GraphLibs
 **/
/*一部かきおとしている。そこだけ直せば多分動く。*/
/*page: グリッドのはしから順番に多角形を生成していく時に、現在見ている層と、その隣の層以外の情報は必要ないから、その2層にそれぞれ0と1という番号を振ってある。できるだけ余計な計算が必要ないように作ってあるが、そのせいで読みにくい点が多々ある。*/
/*memory usage reduced*/
#include <ctype.h>
#include	<stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "cont3.h"
/*NewPointに法線を追加した。ちゃんと動くかな*/


/*for contour*/
extern float 
  grid(int,int,int);
extern int gx,gy,gz;

Point **edge_x,**edge_y,**edge_z,**edge_g;
#define EdgeX(x,y,p) edge_x[((x)*gy+(y))*2+(p)]
#define EdgeY(x,y,p) edge_y[((x)*gy+(y))*2+(p)]
#define EdgeZ(x,y) edge_z[(x)*gy+(y)]
#define EdgeG(x,y,p) edge_g[((x)*gy+(y))*2+(p)]

/*
Point *
  edgex[GRID-1][GRID][2];
Point *
  edgey[GRID][GRID-1][2];
Point *
  EdgeZ(GRID][GRID];
Point *
  edgeG[GRID][GRID][2];
*/

/*Face dummyface;/*dummy first object of chain list*/
/*Point dummypoint;*/
Face *facelist=NULL;
Point *pointlist=NULL;
int npoint=0,nface=0;

int neibor[12][3][3]={
    -1,-1,-1,11, 3, 2, 1, 9,10,
    2, 4, 5,-1,-1,-1, 9,10, 0,
    4, 5, 1, 0,11, 3,-1,-1,-1,
    -1,-1,-1, 2, 0,11, 7, 6, 4,
    5, 1, 2,-1,-1,-1, 3, 7, 6,
    1, 2, 4, 6, 8, 9,-1,-1,-1,
    -1,-1,-1, 8, 9, 5, 4, 3, 7,
    11,10, 8,-1,-1,-1, 6, 4, 3,
    7,11,10, 9, 5, 6,-1,-1,-1,
    -1,-1,-1, 5, 6, 8,10, 0, 1,
    8, 7,11,-1,-1,-1, 0, 1, 9,
    10, 8, 7, 3, 2, 0,-1,-1,-1,};

float
  Proportion(float start,float end,float threshold)
{
    float Return;
    if(end==start)return -1.0;
    Return= (threshold-start)/(end-start);
    return (Return>1.0) ? -1.0 : Return ;
}

/*
Point *
  NewPoint(float x,float y,float z)
{
    Point *newpoint;
    newpoint = malloc(sizeof(Point));
    curpoint->next = newpoint;
    curpoint = newpoint;
    newpoint->org.coord[0] = x;
    newpoint->org.coord[1] = y;
    newpoint->org.coord[2] = z;
    newpoint->next=NULL;
    npoint++;
}
*/
Point *
  NewPoint(float x,float y,float z,float nx,float ny,float nz)
{
    Point *newpoint;
    newpoint = malloc(sizeof(Point));
    newpoint->next = pointlist;
    pointlist = newpoint;
    newpoint->org.coord[0] = x;
    newpoint->org.coord[1] = y;
    newpoint->org.coord[2] = z;
    newpoint->norm.coord[0] = nx;
    newpoint->norm.coord[1] = ny;
    newpoint->norm.coord[2] = nz;
/*    fprintf(stderr,"p %f,%f,%f\n",x,y,z);*/
    npoint++;
    return newpoint;
}

Face *
  NewFace(int n,Point **point,Point *center)
{
    int i;
    Face *newface;
    Point **v;
    nface++;
    newface = (Face *)malloc(sizeof(Face));
    newface -> next = facelist;
    facelist = newface;
    newface -> nvertex = n;
    newface -> center = center;
    newface -> point = (Point **)malloc(n*sizeof(Point *));
    v = newface->point;
    for(i=0;i<n;i++)
      newface->point[i] = point[i];
    return newface;
}

void
MakeEdgeX(int page,int az,float threshold)
{
    int x,y;
    for(x=0;x<gx-1;x++)
      for(y=0;y<gy;y++)
	{
	    float p;
	    p = Proportion(grid(x,y,az),grid(x+1,y,az),threshold);
	    if(p>=0)
	      {
		  float nx,ny,nz;
/*                  fprintf(stderr,"x %d %d %d %f\n",x,y,az,p);*/
		  nx = grid(x+1,y,az)-grid(x,y,az);
		  if(y!=gy-1)
		    ny = p*(grid(x+1,y+1,az)-grid(x+1,y,az))+
		      (1-p)*(grid(x,y+1,az)-grid(x,y,az));
		  else
		    ny=0;
		  if(az!=gz-1)
		    nz = p*(grid(x+1,y,az+1)-grid(x+1,y,az))+
		      (1-p)*(grid(x,y,az+1)-grid(x,y,az));
		  else
		    nz=0;
		  EdgeX(x,y,page) = NewPoint(p+x,y,az,nx,ny,nz);
	      }
	    else
	      EdgeX(x,y,page) = NULL;
	}
}

void
MakeEdgeY(int page,int az,float threshold)
{
    int x,y;
    for(x=0;x<gx;x++)
      for(y=0;y<gy-1;y++)
	{
	    float p;
	    p = Proportion(grid(x,y,az),grid(x,y+1,az),threshold);
	    if(p>=0)
	      {
		  float nx,ny,nz;
/*                  fprintf(stderr,"y %d %d %d %f\n",x,y,az,p);*/
		  if(x!=gx-1)
		    nx = p*(grid(x+1,y+1,az)-grid(x,y+1,az))+
		      (1-p)*(grid(x+1,y,az)-grid(x,y,az));
		  else
		    nx=0;
		  ny = grid(x,y+1,az)-grid(x,y,az);
		  if(az!=gz-1)
		    nz = p*(grid(x,y+1,az+1)-grid(x,y+1,az))+
		      (1-p)*(grid(x,y,az+1)-grid(x,y,az));
		  else
		    nz=0;
		  EdgeY(x,y,page) = NewPoint(x,p+y,az,nx,ny,nz);
	      }
	    else
	      EdgeY(x,y,page) = NULL;
	}
}

void
MakeEdgeZ(int az,float threshold)
{
    int x,y;
    for(x=0;x<gx;x++)
      for(y=0;y<gy;y++)
	{
	    float p;
	    p = Proportion(grid(x,y,az),grid(x,y,az+1),threshold);
	    if(p>=0)
	      {
		  float nx,ny,nz;
                  if((x==40)&&(y==28))
                    fprintf(stderr,"z %d %d %d %f %d %d\n",x,y,az,p,gx,gy);
		  if(x!=gx-1)
		    nx = p*(grid(x+1,y,az+1)-grid(x,y,az+1))+
		      (1-p)*(grid(x+1,y,az)-grid(x,y,az));
		  else
		    nx=0;
		  if(y!=gy-1)
		    ny = p*(grid(x,y+1,az+1)-grid(x,y,az+1))+
		      (1-p)*(grid(x,y+1,az)-grid(x,y,az));
		  else
		    ny=0;
		  nz = grid(x,y,az+1)-grid(x,y,az);
		  EdgeZ(x,y) = NewPoint(x,y,p+az,nx,ny,nz);
	      }
	    else
	      EdgeZ(x,y) = NULL;
	}
}

void
MakeEdgeG(int page,int az,float threshold,int fillbelow)
{
    int x,y;
    for(x=0;x<gx;x++)
      for(y=0;y<gy;y++)
	{
          int v;
          if ( fillbelow ){
            v = (grid(x,y,az)<threshold);
          }
          else{
            v = (grid(x,y,az)>threshold);
          }
	    if(v)
	      EdgeG(x,y,page) = NewPoint(x,y,az,0,0,0);
	    else
	      EdgeG(x,y,page) = NULL;
	}
}


void
  MakePointList(int page,int z,int mode,float threshold)
{
    if((mode&(CROSSY|CROSSZ|SURFACE))!=0)
      MakeEdgeX(page,z,threshold);
    if((mode&(CROSSX|CROSSZ|SURFACE))!=0)
      MakeEdgeY(page,z,threshold);
    if((mode&(CROSSX|CROSSY|SURFACE))!=0)
      MakeEdgeZ(z-1,threshold);
    if((mode&(CROSSX|CROSSY|CROSSZ))!=0)
      MakeEdgeG(page,z,threshold,mode&FILLBELOW);
}

void
  Square_Clean(Square *square)
{
    square->nvertice=0;
}

void *
Square_Contour(Square *square)
{
    int i,edge,face,neib;
    Point **v;
    Face *newface;
    Square_Clean(square);
    /*	Search start point*/
    for(edge=0;edge<8;edge++){
	if(square->cutpoint[edge]!=NULL){
	    square->nvertice++;
	}	
    }    
    if(square->nvertice>2)
      {
	  int j=0;
	  Point *newcutpoint[8];
	  for(i=0;i<8;i++)
	    if(square->cutpoint[i]!=NULL)
	      newcutpoint[j++]=square->cutpoint[i];
	  NewFace(square->nvertice,newcutpoint,square->center);
      }
}

void
  Cube_Clean(Cube *cube)
{
    memset(cube->marks,0,sizeof(int)*12);
    cube->nvertice=0;
}

void
  Cube_Mark(Cube *cube,int edge)
{
    cube->order[cube->nvertice++]=edge;
    cube->marks[edge]=TRUE;
}

void Cube_Next(Cube *cube,int face,int edge)
{
    int e,f;
    if(cube->marks[edge]) return;
    for(f=0;f<3;f++){
	if( (f!=face) && (neibor[edge][f][0]>=0) ){
	    for(e=0;e<3;e++){
		int next;
		if((next=neibor[edge][f][e])>=0)
		  if(cube->cutpoint[next]!=NULL){
		      Cube_Mark(cube,edge);
		      Cube_Next(cube,f,next);
		      return;
		  }
	    }
	}
    }
}


void *
Cube_Contour(Cube *cube)
{
    int i,edge,face,neib;
    Point **v;
    Face *newface;
    Cube_Clean(cube);
    for(edge=0;edge<12;edge++){
        /*if start point is found,*/
	if(cube->cutpoint[edge]!=NULL){
/*            fprintf(stderr,"start: %d\n",edge);*/
	    for(face=0;face<3;face++){
		for(neib=0;neib<3;neib++){
		    int next;
		    if((next=neibor[edge][face][neib])>=0)
		      if(cube->cutpoint[next]!=NULL){
/*                          fprintf(stderr,"next: %d\n",next);*/
			  Cube_Mark(cube,edge);
			  Cube_Next(cube,face,next);
			  goto ContourExit;
		      }
		}
	    }
	}
    }
  ContourExit:
    if(cube->nvertice>2)
      {
	  Point *newcutpoint[12];
	  for(i=0;i<cube->nvertice;i++)
	    {
		newcutpoint[i] = cube->cutpoint[cube->order[i]];
	    }
	  NewFace(cube->nvertice,newcutpoint,newcutpoint[0]);
      }
}

void *
Cube_Contour2(Cube *cube)
{
    int i;
    int n=0;
    Point *newcutpoint[12];
    for(i=0;i<12;i++)
      {
          if(cube->cutpoint[i]!=NULL)
            {
                newcutpoint[n]=cube->cutpoint[i];
                n++;
            }
      }
    if(n){
/*        fprintf(stderr,"%d\n",n);*/
        NewFace(n,newcutpoint,newcutpoint[0]);
    }
}

void
  MakeAFace(int x,int y,int page,int z,int mode,float threshold)
{
    Square square;
    Cube cube;
/*z plane*/
    if(mode&CROSSZ)
      {
          square.cutpoint[0] = EdgeG(x,y,page);
          square.cutpoint[2] = EdgeG(x+1,y,page);
          square.cutpoint[4] = EdgeG(x+1,y+1,page);
          square.cutpoint[6] = EdgeG(x,y+1,page);
          square.cutpoint[1] = EdgeX(x,y,page);
          square.cutpoint[3] = EdgeY(x+1,y,page);
          square.cutpoint[5] = EdgeX(x,y+1,page);
          square.cutpoint[7] = EdgeY(x,y,page);
          square.center = NewPoint(x+0.5,y+0.5,z,0,0,0);
          Square_Contour(&square);
      }
/*y plane*/
    if(mode&CROSSY)
      {
          square.cutpoint[0] = EdgeG(x,y,page);
          square.cutpoint[2] = EdgeG(x+1,y,page);
          square.cutpoint[4] = EdgeG(x+1,y,1-page);
          square.cutpoint[6] = EdgeG(x,y,1-page);
          square.cutpoint[1] = EdgeX(x,y,page);
          square.cutpoint[3] = EdgeZ(x+1,y);
          square.cutpoint[5] = EdgeX(x,y,1-page);
          square.cutpoint[7] = EdgeZ(x,y);
          square.center = NewPoint(x+0.5,y,z-0.5,0,0,0);
          Square_Contour(&square);
      }
    /*x plane*/
    if(mode&CROSSX)
      {
          square.cutpoint[0] = EdgeG(x,y,page);
          square.cutpoint[2] = EdgeG(x,y+1,page);
          square.cutpoint[4] = EdgeG(x,y+1,1-page);
          square.cutpoint[6] = EdgeG(x,y,1-page);
          square.cutpoint[1] = EdgeY(x,y,page);
          square.cutpoint[3] = EdgeZ(x,y+1);
          square.cutpoint[5] = EdgeY(x,y,1-page);
          square.cutpoint[7] = EdgeZ(x,y);
          square.center = NewPoint(x,y+0.5,z-0.5,0,0,0);
          Square_Contour(&square);
      }
    if(mode&SURFACE)
      {
          cube.cutpoint[0] = EdgeX(x,y,0);
          cube.cutpoint[3] = EdgeX(x,y,1);
          cube.cutpoint[6] = EdgeX(x,y+1,1);
          cube.cutpoint[9] = EdgeX(x,y+1,0);
          cube.cutpoint[1] = EdgeY(x,y,0);
          cube.cutpoint[4] = EdgeY(x,y,1);
          cube.cutpoint[7] = EdgeY(x+1,y,1);
          cube.cutpoint[10]= EdgeY(x+1,y,0);
          cube.cutpoint[2] = EdgeZ(x,y);
          cube.cutpoint[5] = EdgeZ(x,y+1);
          cube.cutpoint[8] = EdgeZ(x+1,y+1);
          cube.cutpoint[11]= EdgeZ(x+1,y);
          /*平成１１年１月１３日(水)置換    Cube_Contour(&cube);*/
          Cube_Contour(&cube);
      }
}


void
  MakeFaceList(int page,int z,int mode,float threshold)
{
    int x,y;
    for(x=0;x<gx-1;x++)
      for(y=0;y<gy-1;y++)
	MakeAFace(x,y,page,z,mode,threshold);
}


void safe_free( void* p, char* msg )
{
  //printf( "%x %s\n", p, msg );
  free(p);
}


void FreeList()
{
  int i;
  Face *fo,*f=facelist;
  Point *po,*p=pointlist;
  /*memory leak*/
  //safe_free(edge_x,"ex");
  //safe_free(edge_y,"ey");
  //safe_free(edge_z,"ez");
  //safe_free(edge_g,"eg");
  while(f!=NULL){
    fo=f;
    f=f->next;
    safe_free(fo->point,"fopo");
    safe_free(fo,"fo");
  }
  while(p!=NULL){
    po=p;
    p=p->next;
    safe_free(po,"po");
  }
  pointlist=NULL;
  facelist=NULL;
  nface=0;
  npoint=0;
}


void
  MakeList(int mode,float threshold)
{
    int i,x,y,z,page=0;
    fprintf(stderr,"Threshold:%f\n",threshold);
    edge_x = (Point **)malloc(sizeof(Point *)*gx*gy*2);
    edge_y = (Point **)malloc(sizeof(Point *)*gx*gy*2);
    edge_z = (Point **)malloc(sizeof(Point *)*gx*gy*2);
    edge_g = (Point **)malloc(sizeof(Point *)*gx*gy*2);
    /*基底面のグリッド上の等高線を生成する。*/
    MakeEdgeX(page,0,threshold);
    MakeEdgeY(page,0,threshold);
    MakeEdgeG(page,0,threshold,mode&FILLBELOW);
    /*いまのところ、一番端の面は描かない。*/
    for(z=1;z<gz;z++)
      {
	  page = 1-page;
	  MakePointList(page,z,mode,threshold);
	  MakeFaceList(page,z,mode,threshold);
      }
    fprintf(stderr,"Number of Points:%d\nNumber of Faces:%d\nThreshold:%f\n"
	    ,npoint,nface,threshold);
    /*平成13年10月19日(金)メモリリーク*/
    safe_free(edge_x,"ex2");
    safe_free(edge_y,"ey2");
    safe_free(edge_z,"ez2");
    safe_free(edge_g,"eg2");
}


