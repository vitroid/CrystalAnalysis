#!/usr/bin/env python
# coding: utf-8

#@FRAGを読みこみ、共通な頂点が3つ以上あれば隣接しているとみなしてNGPHを生成する。
#メタンハイドレートにおける正四面体の隣接関係を調べるためのプログラムなので、ほかの系でそのまま使ってはいけない。

import sys
import math
import string


def common(aa,bb):
    ap = 0
    bp = 0
    ncommon = 0
    while True:
        if len(aa) == ap or len(bb) == bp:
            return ncommon
        if aa[ap] == bb[bp]:
            ncommon += 1
            ap += 1
            bp += 1
        elif aa[ap] > bb[bp]:
            bp += 1
        else:
            ap += 1




while True:
    line = sys.stdin.readline()
    if line == "":
        break
    columns = line.split()
    if columns[0] == "@FRAG":
        line = sys.stdin.readline()
        poly = []
        while True:
            line = sys.stdin.readline()
            if line == "":
                break
            n = map(int,line.split())
            n.sort()
            if n[0] < 0:
                break
            poly.append(n)
        tri = dict()
        print "@NGPH"
        print len(poly)
        for i in range(len(poly)):
            #register all triangles
            p = poly[i]
            for t in ((p[0],p[1],p[2]),(p[0],p[1],p[3]),(p[0],p[2],p[3]),(p[1],p[2],p[3])):
                if not tri.has_key(t):
                    tri[t] = set()
                if len(tri[t]) > 0:
                    for j in tri[t]:
                        print j,i
                tri[t].add(i)
        print "-1 -1"
