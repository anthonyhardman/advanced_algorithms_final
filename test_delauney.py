
from turn_in.delauney import Delauney, Triangle
from turn_in.quad_edge import Site


def test_edge():
    sites = [Site(0,0), Site(0,1)]
    d = Delauney(sites)

    assert d.left.origin == sites[0]
    assert d.left.dest == sites[1]

    len(d.find_triangles()) == 0

    circumcenters, voronoi_edges = d.voronoi()

    assert len(circumcenters) == 0
    assert len(voronoi_edges) == 0

def test_triangle():
    sites = [Site(0,0), Site(0,1), Site(1,0)]
    d = Delauney(sites)
    
    triangles = d.find_triangles()
    assert len(triangles) == 1

    assert Triangle(sites[0], sites[1], sites[2]) in triangles

    circumcenters, voronoi_edges = d.voronoi()

    assert len(circumcenters) == 1
    assert len(voronoi_edges) == 0

def test_square():
    sites = [Site(0,0), Site(0,1), Site(1,0), Site(1,1)]
    d = Delauney(sites)

    triangles = d.find_triangles()
    assert len(triangles) == 2

    assert Triangle(sites[0], sites[1], sites[2]) in triangles
    assert Triangle(sites[1], sites[2], sites[3]) in triangles

    circumcenters, voronoi_edges = d.voronoi()

    assert len(circumcenters) == 2
    assert len(voronoi_edges) == 1

def test_square_with_center_dot():
    sites = [Site(0,0), Site(0,1), Site(0.5, 0.5), Site(1,0), Site(1,1)]
    d = Delauney(sites)

    triangles = d.find_triangles()
    assert len(triangles) == 4

    assert Triangle(sites[0], sites[1], sites[2]) in triangles
    assert Triangle(sites[1], sites[2], sites[4]) in triangles
    assert Triangle(sites[0], sites[2], sites[3]) in triangles
    assert Triangle(sites[2], sites[3], sites[4]) in triangles

    circumcenters, voronoi_edges = d.voronoi()

    assert len(circumcenters) == 4
    assert len(voronoi_edges) == 4