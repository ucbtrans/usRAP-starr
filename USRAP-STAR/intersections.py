import networkx as nx
import osmnx as ox

def extract_intersections_without_elevation(
    graph,
    road_list=None
):
    """
    Finds the coordinates of the intersections in the system or of certain 
    roads in the system, along with the bearing of the points. 

    Parameters
    -------
    graph : Networkx.MultiDiGraph
        input graph
    road_list : string or list
        certain road(s) that will only be analyzed

    Returns
    -------

    """
    return

def extract_intersections_with_elevation(
    graph,
    API_key,
    road_list=None
):
    """
    Finds the coordinates of the intersections in the system or of certain 
    roads in the system, along with the bearing and elevation of the points. 

    Parameters
    -------
    graph : Networkx.MultiDiGraph
        input graph
    API_key : string
        the key to interact with the Google elevation API
    road_list : string or list
        certain road(s) that will only be analyzed

    Returns
    -------
    dict where the keys are the road names and the values
    """
    return