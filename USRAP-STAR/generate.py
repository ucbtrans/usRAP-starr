from math import trunc
import string
import networkx as nx
import osmnx as ox
import copy

def generate_graph_from_place(
    query, 
    network_type='all_private', 
    simplify=True, retain_all=False, 
    truncate_by_edge=False, 
    which_result=None, 
    buffer_dist=None, 
    clean_periphery=True, 
    custom_filter=None, 
    road_list=None,
):
    """
    Create graph from OSM within the boundaries of some geocodable place(s).

    The query must be geocodable and OSM must have polygon boundaries for the
    geocode result. If OSM does not have a polygon for this place, you can
    instead get its street network using the graph_from_address function,
    which geocodes the place name to a point and gets the network within some
    distance of that point.

    If OSM does have polygon boundaries for this place but you're not finding
    it, try to vary the query string, pass in a structured query dict, or vary
    the which_result argument to use a different geocode result. If you know
    the OSM ID of the place, you can retrieve its boundary polygon using the
    geocode_to_gdf function, then pass it to the graph_from_polygon function.
    Parameters
    ----------
    query : string or dict or list
        the query or queries to geocode to get place boundary polygon(s)
    network_type : string {"all_private", "all", "bike", "drive", "drive_service", "walk"}
        what type of street network to get if custom_filter is None
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside boundary polygon if at least one of
        node's neighbors is within the polygon
    which_result : int
        which geocoding result to use. if None, auto-select the first
        (Multi)Polygon or raise an error if OSM doesn't return one.
    buffer_dist : float
        distance to buffer around the place geometry, in meters
    clean_periphery : bool
        if True, buffer 500m to get a graph larger than requested, then
        simplify, then truncate it to requested spatial boundaries
    custom_filter : string
        a custom ways filter to be used instead of the network_type presets
        e.g., '["power"~"line"]' or '["highway"~"motorway|trunk"]'. Also pass
        in a network_type that is in settings.bidirectional_network_types if
        you want graph to be fully bi-directional.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_place(
        query, 
        network_type=network_type, 
        simplify=simplify, 
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        which_result=which_result, 
        buffer_dist=buffer_dist, 
        clean_periphery=clean_periphery, 
        custom_filter=custom_filter,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def generate_graph_from_address(
    address, 
    dist=1000, 
    dist_type='bbox', 
    network_type='all_private', 
    simplify=True, 
    retain_all=False, 
    truncate_by_edge=False, 
    return_coords=False, 
    clean_periphery=True, 
    custom_filter=None,
    road_list=None,
):
    """
    Create a graph from OSM within some distance of some address.

    Parameters
    ----------
    address : string
        the address to geocode and use as the central point around which to
        construct the graph
    dist : int
        retain only those nodes within this many meters of the center of the
        graph
    dist_type : string {"network", "bbox"}
        if "bbox", retain only those nodes within a bounding box of the
        distance parameter. if "network", retain only those nodes within some
        network distance from the center-most node (requires that scikit-learn
        is installed as an optional dependency).
    network_type : string {"all_private", "all", "bike", "drive", "drive_service", "walk"}
        what type of street network to get if custom_filter is None
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside bounding box if at least one of node's
        neighbors is within the bounding box
    return_coords : bool
        optionally also return the geocoded coordinates of the address
    clean_periphery : bool,
        if True, buffer 500m to get a graph larger than requested, then
        simplify, then truncate it to requested spatial boundaries
    custom_filter : string
        a custom ways filter to be used instead of the network_type presets
        e.g., '["power"~"line"]' or '["highway"~"motorway|trunk"]'. Also pass
        in a network_type that is in settings.bidirectional_network_types if
        you want graph to be fully bi-directional.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    networkx.MultiDiGraph or optionally (networkx.MultiDiGraph, (lat, lng))
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_address(
        address, 
        dist=dist, 
        dist_type=dist_type, 
        network_type=network_type, 
        simplify=simplify, 
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        return_coords=return_coords, 
        clean_periphery=clean_periphery, 
        custom_filter=custom_filter,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def generate_graph_from_bbox(
    north, 
    south, 
    east, 
    west, 
    network_type='all_private', 
    simplify=True, 
    retain_all=False, 
    truncate_by_edge=False, 
    clean_periphery=True, 
    custom_filter=None,
    road_list=None,
):
    """
    Create a graph from OSM within some bounding box.

    Parameters
    ----------
    north : float
        northern latitude of bounding box
    south : float
        southern latitude of bounding box
    east : float
        eastern longitude of bounding box
    west : float
        western longitude of bounding box
    network_type : string {"all_private", "all", "bike", "drive", "drive_service", "walk"}
        what type of street network to get if custom_filter is None
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside bounding box if at least one of node's
        neighbors is within the bounding box
    clean_periphery : bool
        if True, buffer 500m to get a graph larger than requested, then
        simplify, then truncate it to requested spatial boundaries
    custom_filter : string
        a custom ways filter to be used instead of the network_type presets
        e.g., '["power"~"line"]' or '["highway"~"motorway|trunk"]'. Also pass
        in a network_type that is in settings.bidirectional_network_types if
        you want graph to be fully bi-directional.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_bbox(
        north, 
        south, 
        east, 
        west, 
        network_type=network_type, 
        simplify=simplify, 
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        clean_periphery=clean_periphery, 
        custom_filter=custom_filter,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def generate_graph_from_point(
    center_point, 
    dist=1000, 
    dist_type='bbox', 
    network_type='all_private', 
    simplify=True, 
    retain_all=False, 
    truncate_by_edge=False, 
    clean_periphery=True, 
    custom_filter=None,
    road_list=None,
):
    """
    Create a graph from OSM within some distance of some (lat, lng) point.

    Parameters
    ----------
    center_point : tuple
        the (lat, lng) center point around which to construct the graph
    dist : int
        retain only those nodes within this many meters of the center of the
        graph, with distance determined according to dist_type argument
    dist_type : string {"network", "bbox"}
        if "bbox", retain only those nodes within a bounding box of the
        distance parameter. if "network", retain only those nodes within some
        network distance from the center-most node (requires that scikit-learn
        is installed as an optional dependency).
    network_type : string, {"all_private", "all", "bike", "drive", "drive_service", "walk"}
        what type of street network to get if custom_filter is None
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside bounding box if at least one of node's
        neighbors is within the bounding box
    clean_periphery : bool,
        if True, buffer 500m to get a graph larger than requested, then
        simplify, then truncate it to requested spatial boundaries
    custom_filter : string
        a custom ways filter to be used instead of the network_type presets
        e.g., '["power"~"line"]' or '["highway"~"motorway|trunk"]'. Also pass
        in a network_type that is in settings.bidirectional_network_types if
        you want graph to be fully bi-directional.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_point(
        center_point, 
        dist=dist, 
        dist_type=dist_type, 
        network_type=network_type, 
        simplify=simplify, 
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        clean_periphery=clean_periphery, 
        custom_filter=custom_filter,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def generate_graph_from_polygon(
    polygon, 
    network_type='all_private', 
    simplify=True, 
    retain_all=False, 
    truncate_by_edge=False, 
    clean_periphery=True, 
    custom_filter=None,
    road_list=None,
):
    """
    Create a graph from OSM within the boundaries of some shapely polygon.

    Parameters
    ----------
    polygon : shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        the shape to get network data within. coordinates should be in
        unprojected latitude-longitude degrees (EPSG:4326).
    network_type : string {"all_private", "all", "bike", "drive", "drive_service", "walk"}
        what type of street network to get if custom_filter is None
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside boundary polygon if at least one of
        node's neighbors is within the polygon
    clean_periphery : bool
        if True, buffer 500m to get a graph larger than requested, then
        simplify, then truncate it to requested spatial boundaries
    custom_filter : string
        a custom ways filter to be used instead of the network_type presets
        e.g., '["power"~"line"]' or '["highway"~"motorway|trunk"]'. Also pass
        in a network_type that is in settings.bidirectional_network_types if
        you want graph to be fully bi-directional.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_polygon(
        polygon, 
        network_type=network_type,
        simplify=simplify,
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        clean_periphery=clean_periphery, 
        custom_filter=custom_filter,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def generate_graph_from_xml_file(
    filepath, 
    bidirectional=False, 
    simplify=True, 
    retain_all=False,
    road_list=None,
):
    """
    Create a graph from data in a .osm formatted XML file.

    Parameters
    ----------
    filepath : string or pathlib.Path
        path to file containing OSM XML data
    bidirectional : bool
        if True, create bi-directional edges for one-way streets
    simplify : bool
        if True, simplify graph topology with the `simplify_graph` function
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    road_list : string
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
    """
    #Generate the graph using osmnx using the parameters
    graph = ox.graph_from_xml(
        filepath, 
        bidirectional=bidirectional, 
        simplify=simplify, 
        retain_all=retain_all,
    )
    graph = ox.get_undirected(ox.get_digraph(graph))
    #Remove edges that do not have their name in road_list
    if road_list:
        graph = _isolate_road(graph, road_list)
    return graph

def _isolate_road(
    graph, 
    road,
):
    """
    Removes all the edges that do not have an edge attribute 'name', or the value
    attributed to the key, 'name', does not contain a string that is in the road_list

    Parameters
    -------
    graph : Networkx.MultiDiGraph
        input graph
    road_list : string
        the road to remain in the graph

    Returns
    -------
    graph : Networkx.MultiDiGraph
    """
    nodeRemover = []
    #Removing all the edges in the graph that do not have edges that contain the road name
    for i in graph:
        for j in graph[i]:
            for k in graph[i][j]:
                if graph[i][j][0].get('name') == None:
                    nodeRemover.append((i, j))
                    continue
                elif type(graph[i][j][0]['name']) == list and graph[i][j][0]['name'].count(road) == 0:
                    nodeRemover.append((i, j))
                elif graph[i][j][0]['name'] != road:
                    nodeRemover.append((i, j))
    while(len(nodeRemover)>0) :
        a = nodeRemover.pop()
        if graph[a[0]].get(a[1]) != None:
            graph.remove_edge(a[0], a[1])
    #Removing all isolated vertices of the Graph
    for i in graph:
        if len(graph[i]) == 0:
            nodeRemover.append(i)
    while(len(nodeRemover) > 0):
        x = nodeRemover.pop()
        graph.remove_node(x)
    return graph


