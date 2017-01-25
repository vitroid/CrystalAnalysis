def line(x,y,z,a,b,c):
    return "l {0} {1} {2} {3} {4} {5} \n".format(x,y,z,a,b,c)

#Stick is a line with own width and arrowheads
def stick(x,y,z,a,b,c):
    return "s {0} {1} {2} {3} {4} {5} \n".format(x,y,z,a,b,c)

def circle(x,y,z):
    return "c {0} {1} {2}\n".format(x,y,z)

def palette(p):
    return "@ {0}\n".format(p)

def layer(y):
    return "y {0}\n".format(y)

def radius(r):
    return "r {0}\n".format(r)

def text(x,y,z,msg):
    return "t {0} {1} {2} {3}\n".format(x,y,z,msg)
