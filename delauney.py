from collections import defaultdict
import itertools
from typing import Dict, List, Tuple
import uuid

import numpy as np

from quad_edge import QuadEdge, Site

class Triangle:
    def __init__(self, a: Site, b: Site, c: Site) -> None:
        self.sites = tuple(sorted([a, b, c], key=lambda site: (site.x, site.y)))

    def __eq__(self, other):
        return self.sites == other.sites

    def __hash__(self):
        return hash(self.sites)

    def __repr__(self):
        return f"Triangle({self.sites[0]}, {self.sites[1]}, {self.sites[2]})"

class VoronoiEdge:
    def __init__(self, origin: Site, dest: Site) -> None:
        self.id = str(uuid.uuid4())
        self.origin = origin
        self.dest = dest

    def __repr__(self):
        return f"VoronoiEdge(start={self.origin}, end={self.end})"

class Delauney:
    def __init__(self, sites: List[Site]) -> None:
        self.edges: Dict[str, QuadEdge] = {}
        self.left: QuadEdge = None
        self.right: QuadEdge = None
        sites.sort(key=lambda s: (s.x, s.y))
        self.left, self.right = self.__triangulate(sites)

    def voronoi(self):
        triangles = self.find_triangles()
        triangle_to_circumcenter = {triangle: self.circumcenter(*triangle.sites) for triangle in triangles}

        edge_to_triangles = defaultdict(list)
        for triangle in triangles:
            for site1, site2 in itertools.combinations(triangle.sites, 2):
                edge_key = frozenset((site1, site2))
                edge_to_triangles[edge_key].append(triangle)

        voronoi_edges = set()

        for adjacent in edge_to_triangles.values():
            if len(adjacent) == 2:  
                t1, t2 = adjacent
                cc1 = triangle_to_circumcenter[t1]
                cc2 = triangle_to_circumcenter[t2]
                voronoi_edges.add(VoronoiEdge(cc1, cc2))

        return list(triangle_to_circumcenter.values()), list(voronoi_edges)

    def circumcenter(self, a: Site, b: Site, c: Site) -> Site:
        ax, ay = a.x, a.y
        bx, by = b.x, b.y
        cx, cy = c.x, c.y

        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

        if abs(d) < 1e-10: 
            raise ValueError("Cannot compute circumcenter of collinear points")

        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d

        return Site(ux, uy)

    def __triangulate(self, sites: List[Site]) -> Tuple[QuadEdge, QuadEdge]:
        # Base case: Only 2 sites, create a single edge
        if len(sites) == 2:
            a = self.make_edge(sites[0], sites[1])
            return (a, a.sym)
        
        # Base case: 3 sites, create a triangle
        elif len(sites) == 3:
            a = self.make_edge(sites[0], sites[1])
            b = self.make_edge(sites[1], sites[2])

            self.splice(a.sym, b)

            if self.ccw(sites[0], sites[1], sites[2]):
                c = self.connect(b, a)
                return (a, b.sym)
            elif self.ccw(sites[0], sites[2], sites[1]):
                c = self.connect(b, a)
                return (c.sym, c)
            else:
                return (a, b.sym)
        
        # Recursive case: More than 3 sites
        n = len(sites)
        (ldo, ldi) = self.__triangulate(sites[: n // 2])
        (rdi, rdo) = self.__triangulate(sites[n // 2 :])

        # Merge step: Find the lower common tangent
        # -----------------------------------------
        while True:
            if self.left_of(rdi.origin, ldi):
                ldi = ldi.lnext
            elif self.right_of(ldi.origin, rdi):
                rdi = rdi.rprev
            else:
                break
        
        # Connect the left and right triangulations
        base1 = self.connect(rdi.sym, ldi)

        # Adjust edges if necessary
        if ldi.origin == ldo.origin:
            ldo = base1.sym
        if rdi.origin == rdo.origin:
            rdo = base1

        def valid(e):
            return self.right_of(e.dest, base1)

        # Stitch together left and right triangulations until the upper common tangent is found
        while True:
            lcand = base1.sym.onext
            # If left candidate does not follow the delauney condition, delete it and try with the next one
            if valid(lcand):
                while self.in_circle(base1.dest, base1.origin, lcand.dest, lcand.onext.dest):
                    t = lcand.onext
                    self.delete(lcand)
                    lcand = t

            rcand = base1.oprev
            # If right candidate does not follow the delauney condition, delete it and try with the next one
            if valid(rcand):
                while self.in_circle(base1.dest, base1.origin, rcand.dest, rcand.oprev.dest):
                    t = rcand.oprev
                    self.delete(rcand)
                    rcand = t

            # If both candidates are invalid, we have found the upper common tangent
            if not valid(lcand) and not valid(rcand):
                break
            # If right candidate is valid and follows the delauney condition, connect it to the base
            if not valid(lcand) or (
                valid(rcand)
                and self.in_circle(lcand.dest, lcand.origin, rcand.origin, rcand.dest)
            ):
                base1 = self.connect(rcand, base1.sym)
            # If left candidate is valid and follows the delauney condition, connect it to the base
            else:
                base1 = self.connect(base1.sym, lcand.sym)

        # Return the left and right most edges
        return (ldo, rdo)
    
    def in_circle(self, a: Site, b: Site, c: Site, d: Site):
        return (
            np.linalg.det(
                [
                    [a.x, a.y, a.x**2 + a.y**2, 1],
                    [b.x, b.y, b.x**2 + b.y**2, 1],
                    [c.x, c.y, c.x**2 + c.y**2, 1],
                    [d.x, d.y, d.x**2 + d.y**2, 1],
                ]
            )
            > 0
        )


    def ccw(self, a: Site, b: Site, c: Site):
        return np.linalg.det([[a.x, a.y, 1], [b.x, b.y, 1], [c.x, c.y, 1]]) > 0


    def right_of(self, site: Site, edge: QuadEdge):
        return self.ccw(site, edge.dest, edge.origin)


    def left_of(self, site: Site, edge: QuadEdge):
        return self.ccw(site, edge.origin, edge.dest)
    
    def make_edge(self, a: Site, b: Site):
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

        self.edges[e1.id] = e1
        self.edges[e2.id] = e2
        self.edges[e3.id] = e3
        self.edges[e4.id] = e4

        return e1


    def splice(self, a: QuadEdge, b: QuadEdge):
        alpha = a.onext.rot
        beta = b.onext.rot

        t1 = b.onext
        t2 = a.onext
        t3 = beta.onext
        t4 = alpha.onext

        a.onext = t1
        b.onext = t2
        alpha.onext = t3
        beta.onext = t4

        self.edges[a.id] = a
        self.edges[b.id] = b

    def connect(self, a: QuadEdge, b: QuadEdge):
        e = self.make_edge(a.dest, b.origin)
        self.splice(e, a.lnext)
        self.splice(e.sym, b)
        return e
    
    def delete(self, e: QuadEdge):
        self.splice(e, e.oprev)
        self.splice(e.sym, e.sym.oprev)

        self.edges.pop(e.id)
        self.edges.pop(e.sym.id)

    def find_triangles(self):
        triangles = set()
        for e in self.edges.values():
            if e.origin and e.dest:
                if e.lnext.lnext.dest == e.origin:
                    triangles.add(Triangle(e.origin, e.lnext.origin, e.lnext.lnext.origin))
                if e.rnext.rnext.dest == e.origin:
                    triangles.add(Triangle(e.origin, e.rnext.origin, e.rnext.rnext.origin))

        return triangles
