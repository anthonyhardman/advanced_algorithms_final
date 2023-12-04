import numpy as np
from typing import List

class Site:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class QuadEdge:
    def __init__(self) -> None:
        self.origin = None
        self.rot = None
        self.onext = None

    @property
    def dest(self):
        return self.sym.origin

    @property
    def right(self):
        return self.rot.origin

    @property
    def left(self):
        return self.inv_rot().origin

    @property
    def sym(self):
        return self.rot.rot

    @property
    def inv_rot(self):
        return self.sym.rot

    @property
    def lnext(self):
        return self.inv_rot.onext.rot

    @property
    def rnext(self):
        return self.rot.onext.inv_rot

    @property
    def dnext(self):
        return self.sym.onext.sym

    @property
    def oprev(self):
        return self.rot.onext.rot

    @property
    def lprev(self):
        return self.onext.sym

    @property
    def rprev(self):
        return self.sym.onext

    @property
    def dprev(self):
        return self.inv_rot.onext.inv_rot

    @staticmethod
    def make_edge(a: Site, b: Site):
        e1 = QuadEdge()
        e2 = QuadEdge()
        e3 = QuadEdge()
        e4 = QuadEdge()

        e1.origin = a
        e3.origin = b

        e1.rot = e2
        e2.rot = e3
        e3.rot = e4
        e4.rot = e1

        e1.onext = e1
        e2.onext = e4
        e3.onext = e3
        e4.onext = e2

        return e1

    @staticmethod
    def splice(a, b):
        a.onext.rot.onext, b.onext.rot.onext = b.onext.rot.onext, a.onext.rot.onext
        a.onext, b.onext = b.onext, a.onext

    @staticmethod
    def connect(a, b):
        e = QuadEdge.make_edge(a.dest, b.origin)
        QuadEdge.splice(e, a.lnext)
        QuadEdge.splice(e.sym, b)
        return e

    @staticmethod
    def delete(e):
        QuadEdge.splice(e, e.oprev())
        QuadEdge.splice(e.sym, e.sym.oprev())


class Mesh:
    def __init__(self) -> None:
        self.site = None
        self.left = None
        self.right = None


def triangulate(sites: List[Site]) -> Mesh:
    sites.sort(key=lambda s: (s.x, s.y))


def delaunay(sites: List[Site]) -> Mesh:
    if len(sites) == 2:
        edges = Mesh()
        a = QuadEdge.make_edge(sites[0], sites[1])
        edges.left = a
        edges.right = a.sym
        return edges
    if len(sites) == 3:
        return make_ccw_triangle(sites)
    return merge(delaunay(sites[: len(sites) // 2]), delaunay(sites[len(sites) // 2 :]))


def make_ccw_triangle(sites: List[Site]) -> Mesh:
    edges = Mesh()

    a = QuadEdge.make_edge(sites[0], sites[1])
    b = QuadEdge.make_edge(sites[1], sites[2])

    QuadEdge.splice(a.sym, b)
    if ccw(sites[0], sites[1], sites[2]):
        c = QuadEdge.connect(b, a)
        edges.left = a
        edges.right = b.sym
    else:
        if ccw(sites[0], sites[2], sites[1]):
            c = QuadEdge.connect(b, a)
            edges.left = c.sym
            edges.right = c
        else:
            edges.left = a
            edges.right = b.sym

    return edges


def merge(left: Mesh, right: Mesh):
    ldo = left.left
    ldi = left.right
    rdi = left.left
    rdo = left.right

    basel = QuadEdge()
    lcand = QuadEdge()
    rcand = QuadEdge()
    t = QuadEdge()

    edges = Mesh()

    while True:
        if left_of(rdi.origin, ldi):
            ldi = ldi.lnext
            continue
        elif right_of(ldi.origin, rdi):
            rdi = rdi.rprev
            continue
        break

    basel = QuadEdge.connect(rdi.sym, ldi)
    if ldi.origin == ldo.origin:
        ldo = basel.sym
    if rdi.origin == rdo.origin:
        rdo = basel

    while True:
        lcand = basel.sym.onext
        if right_of(lcand.dest, basel):
            while in_circle(basel.dest, basel.orgin, lcand.dest, lcand.onext.dest):
                t = lcand.onext
                QuadEdge.delete(lcand)
                lcand = t

        rcand = basel.oprev
        if right_of(rcand.dest, basel):
            while in_circle(basel.dest, basel.orgin, rcand.dest, rcand.oprev.dest):
                t = rcand.oprev
                QuadEdge.delete(rcand)
                rcand = t

        valid_lcand = ccw(lcand.dest, basel.dest, basel.origin)
        valid_rcand = ccw(rcand.dest, basel.dest, basel.origin)

        if not valid_lcand and not valid_rcand:
            break
        if (
            not valid_lcand
            or not valid_rcand
            and in_circle(lcand.dest, lcand.origin, rcand.origin, rcand.dest)
        ):
            basel = QuadEdge.connect(rcand, basel.sym)
        else:
            basel = QuadEdge.connect(basel.sym, lcand.sym)

    edges.left = ldo
    edges.right = rdo
    return edges



def in_circle(a: Site, b: Site, c: Site, p: Site):
    return (
        np.linalg.det(
            [a.x - p.x, a.y - p.y, (a.x - p.x) ** 2 + (a.y - p.y) ** 2],
            [b.x - p.x, b.y - p.y, (b.x - p.x) ** 2 + (b.y - p.y) ** 2],
            [c.x - p.x, c.y - p.y, (c.x - p.x) ** 2 + (c.y - p.y) ** 2],
        )
        > 0
    )

def ccw(a: Site, b: Site, c: Site):
    return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y) > 0

def left_of(site: Site, edge: QuadEdge):
    return ccw(site, edge.dest, edge.origin)


def right_of(site: Site, edge: QuadEdge):
    return ccw(site, edge.origin, edge.dest)

mesh = delaunay([Site(0, 0), Site(1, 0), Site(0, 1)])