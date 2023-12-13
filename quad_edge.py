
import uuid


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
        self.id = str(uuid.uuid4())
        self.origin: Site = None
        self.rot: QuadEdge = None
        self.onext: QuadEdge = None

    def __str__(self) -> str:
        return f"Edge({self.origin}, {self.dest})"

    def __repr__(self) -> str:
        return f"Edge({self.origin}, {self.dest})"
        
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

        t1 = b.onext
        t2 = a.onext
        t3 = beta.onext
        t4 = alpha.onext

        a.onext = t1
        b.onext = t2
        alpha.onext = t3
        beta.onext = t4

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