
from turn_in.delauney import Delauney
from turn_in.quad_edge import Site


delauney = Delauney()

sites = [Site(0, 0), Site(1, 0), Site(0, 1), Site(1, 1)]
l, r = delauney.__triangulate(sites)
