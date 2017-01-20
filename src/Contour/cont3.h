/*#define GRID     63*/
#define TRUE     1
#define FALSE    0
#define Real     float
/*簡単にx3d用に変換できると思ったが、私の方法では、辺の情報がない。*/
/*hullを利用しようか。*/
typedef struct
{
    float coord[3];
}
Vector3;

typedef struct tmppoint
{
    Vector3 org,norm;
    int x,y;
    float z;
    struct tmppoint *next;
}
Point;

typedef struct tmpface
{
    int nvertex;
    Point **point;
    Point *center;
#ifdef GRADE
    int col;
#endif
    struct tmpface *next;
}
Face;

typedef struct {
    Point *cutpoint[8];
    Point *center;
    int  nvertice;
} Square;

typedef struct {
    Point *cutpoint[12];
    int  marks[12];
    int  nvertice;
    int order[12];
} Cube;

#define SURFACE 0x01
#define CROSSX 0x02
#define CROSSY 0x04
#define CROSSZ 0x08
#define FILLBELOW 0x10
void MakeList(int mode,float threshold);

