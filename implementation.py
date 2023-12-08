from pprint import pprint
import numpy as np
from typing import List, Tuple


class Site:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Site({self.x}, {self.y})"


class QuadEdge:
    def __init__(self) -> None:
        self.origin = None
        self.rot = None
        self.onext = None

    @property
    def oprev(self):
        return self.rot.onext.rot

    @property
    def dest(self):
        return self.sym.origin

    @property
    def right(self):
        return self.rot.origin

    @property
    def left(self):
        return self.inv_rot.origin

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
        alpha = a.onext.rot
        beta = b.onext.rot

        a.onext, b.onext = b.onext, a.onext
        alpha.onext, beta.onext = beta.onext, alpha.onext

    @staticmethod
    def connect(a, b):
        e = QuadEdge.make_edge(a.dest, b.origin)
        QuadEdge.splice(e, a.lnext)
        QuadEdge.splice(e.sym, b)
        return e

    @staticmethod
    def delete(e):
        QuadEdge.splice(e, e.oprev)
        QuadEdge.splice(e.sym, e.sym.oprev)


class Mesh:
    def __init__(self) -> None:
        self.sites: Site = None
        self.left: QuadEdge = None
        self.right: QuadEdge = None


def triangulate(sites: List[Site]) -> Mesh:
    sites.sort(key=lambda s: (s.x, s.y))
    edges = delaunay(sites)
    edges.sites = sites
    return edges


def delaunay(sites: List[Site]) -> Tuple[QuadEdge, QuadEdge]:
    sites.sort(key=lambda s: (s.x, s.y))

    if len(sites) == 2:
        edge = QuadEdge.make_edge(sites[0], sites[1])
        return [edge, edge.sym]
    elif len(sites) == 3:
        a = QuadEdge.make_edge(sites[0], sites[1])
        b = QuadEdge.make_edge(sites[1], sites[2])
        QuadEdge.splice(a.sym, b)

        if ccw(sites[0], sites[1], sites[2]):
            c = QuadEdge.connect(b, a)
            return (a, b.sym)
        elif ccw(sites[0], sites[2], sites[1]):
            c = QuadEdge.connect(b, a)
            return (c.sym, c)
        else:
            return (a, b.sym)

    n = len(sites)
    (ldo, ldi) = delaunay(sites[: n // 2])
    (rdi, rdo) = delaunay(sites[n // 2 :])

    while True:
        if left_of(rdi.origin, ldi):
            ldi = ldi.lnext
        elif right_of(ldi.origin, rdi):
            rdi = rdi.rprev
        else:
            break

    base1 = QuadEdge.connect(rdi.sym, ldi)

    if ldi.origin == ldo.origin:
        ldo = base1.sym
    if rdi.origin == rdo.origin:
        rdo = base1

    def valid(e):
        return right_of(e.dest, base1)

    while True:
        lcand = base1.sym.onext
        if valid(lcand):
            while in_circle(base1.dest, base1.origin, lcand.dest, lcand.onext.dest):
                t = lcand.onext
                QuadEdge.delete(lcand)
                lcand = t

        rcand = base1.oprev
        if valid(rcand):
            while in_circle(base1.dest, base1.origin, rcand.dest, rcand.oprev.dest):
                t = rcand.oprev
                QuadEdge.delete(rcand)
                rcand = t
                
        if not valid(lcand) and not valid(rcand):
            break
        if not valid(lcand) or (valid(lcand) and in_circle(lcand.dest, lcand.origin, rcand.origin, rcand.dest)):
            base1 = QuadEdge.connect(rcand, base1.sym)
        else:
            base1 = QuadEdge.connect(base1.sym, lcand.sym)
    
    return (ldo, rdo)


def in_circle(a: Site, b: Site, c: Site, p: Site):
    return (
        np.linalg.det(
            [
                [a.x, a.y, a.x**2 + a.y**2, 1],
                [b.x, b.y, b.x**2 + b.y**2, 1],
                [c.x, c.y, c.x**2 + c.y**2, 1],
                [p.x, p.y, p.x**2 + p.y**2, 1],
            ]
        )
        > 0
    )


def ccw(a: Site, b: Site, c: Site):
    return np.linalg.det(
        [
            [a.x, a.y, 1], 
            [b.x, b.y, 1], 
            [c.x, c.y, 1]
        ]) > 0


def right_of(site: Site, edge: QuadEdge):
    return ccw(site, edge.dest, edge.origin)


def left_of(site: Site, edge: QuadEdge):
    return ccw(site, edge.origin, edge.dest)


left, right = delaunay([Site(0, 0), Site(1, 0), Site(0, 1), Site(1, 1), Site(0.5, 0.5)])

