import networkx as nx
import osmnx as ox

def interpolate_roads(
    roads,
    distance=1,
    road_list=None
):
    """
    Find equidistant points along the a linestring using distance
    calculations that assume that these are coordinates on Earth.

    Parameters
    -------
    
    """
    return