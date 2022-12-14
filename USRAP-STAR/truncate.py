import string
import networkx as nx
import osmnx as ox
import copy

def truncate_to_polygon(
    graph, 
    polygon, 
    retain_all=False, 
    truncate_by_edge=False, 
    quadrat_width=0.05, 
    min_num=3,
    road_list=None,
):
    """
    Remove every node in graph that falls outside a (Multi)Polygon.
    Remove all edges not in road_list if specified.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        input graph
    polygon : shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        only retain nodes in graph that lie within this geometry
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    truncate_by_edge : bool
        if True, retain nodes outside boundary polygon if at least one of
        node's neighbors is within the polygon
    quadrat_width : numeric
        passed on to intersect_index_quadrats: the linear length (in degrees)
        of the quadrats with which to cut up the geometry (default = 0.05,
        approx 4km at NYC's latitude)
    min_num : int
        passed on to intersect_index_quadrats: the minimum number of linear
        quadrat lines (e.g., min_num=3 would produce a quadrat grid of 4
        squares)
    road_list : string or list
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
        the truncated graph
    """
    truncated = copy.deepcopy(graph)
    truncated = ox.truncate.truncate_graph_polygon(
        truncated, 
        polygon, 
        retain_all=retain_all, 
        truncate_by_edge=truncate_by_edge, 
        quadrat_width=quadrat_width, 
        min_num=min_num,
        )
    #Remove edges that do not have their name in road_list
    if road_list.isinstance(list):
        graph = _isolate_roads(graph, road_list)
    elif road_list.isinstance(string):
        graph = _isolate_road(graph, road_list)

def truncate_to_bbox(
    graph,
    north,
    south,
    east,
    west,
    truncate_by_edge=False,
    retain_all=False,
    quadrat_width=0.05,
    min_num=3,
    road_list=None,
):
    """
    Remove every node in graph that falls outside a bounding box.
    Remove all edges not in road_list if specified.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        input graph
    north : float
        northern latitude of bounding box
    south : float
        southern latitude of bounding box
    east : float
        eastern longitude of bounding box
    west : float
        western longitude of bounding box
    truncate_by_edge : bool
        if True, retain nodes outside bounding box if at least one of node's
        neighbors is within the bounding box
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    quadrat_width : numeric
        passed on to intersect_index_quadrats: the linear length (in degrees) of
        the quadrats with which to cut up the geometry (default = 0.05, approx
        4km at NYC's latitude)
    min_num : int
        passed on to intersect_index_quadrats: the minimum number of linear
        quadrat lines (e.g., min_num=3 would produce a quadrat grid of 4
        squares)
    road_list : string or list
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
        the truncated graph
    """
    truncated = copy.deepcopy(graph)
    truncated = ox.truncate.truncate_by_bbox(
        truncated,
        north,
        south,
        east,
        west,
        truncate_by_edge=truncate_by_edge, 
        retain_all=retain_all,
        quadrat_width=quadrat_width, 
        min_num=min_num,
    )
    #Remove edges that do not have their name in road_list
    if road_list.isinstance(list):
        truncated = _isolate_roads(truncated, road_list)
    elif road_list.isinstance(string):
        truncated = _isolate_road(truncated, road_list)
    return truncated

def truncate_around_node(
    graph, 
    source_node, 
    max_dist=1000, 
    weight="length", 
    retain_all=False,
    road_list=None
):
    """
    Remove every node farther than some network distance from source_node.
    Remove all edges not in road_list if specified. This function can be 
    slow for large graphs, as it must calculate shortest path distances between 
    source_node and every other graph node.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        input graph
    source_node : int
        the node in the graph from which to measure network distances to other
        nodes
    max_dist : int
        remove every node in the graph greater than this distance from the
        source_node (along the network)
    weight : string
        how to weight the graph when measuring distance (default 'length' is
        how many meters long the edge is)
    retain_all : bool
        if True, return the entire graph even if it is not connected.
        otherwise, retain only the largest weakly connected component.
    road_list : string or list
        a filter to only contain certain roads within the graph

    Returns
    -------
    graph : networkx.MultiDiGraph
        the truncated graph
    """
    truncated = copy.deepcopy(graph)
    truncated = ox.truncate.truncate_graph_dist(
        truncated,
        source_node,
        max_dist=max_dist,
        weight=weight,
        retain_all=retain_all,
        road_list=road_list,
    )
    #Remove edges that do not have their name in road_list
    if road_list.isinstance(list):
        truncated = _isolate_roads(truncated, road_list)
    elif road_list.isinstance(string):
        truncated = _isolate_road(truncated, road_list)
    return truncated

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
    road_list : string or list
        the roads to remain in the graph

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

def _isolate_roads(
    graph, 
    road_list,
):
    """
    Removes all the edges that do not have an edge attribute 'name', or the value
    attributed to the key, 'name', does not contain a string that is in the road_list

    Parameters
    -------
    graph : Networkx.MultiDiGraph
        input graph
    road_list : list
        the roads to remain in the graph

    Returns
    -------
    graph : Networkx.MultiDiGraph
    """
    remove_list = []
    #Removing all the edges in the graph that do not have edges that contain the road name
    for i in graph:
        for j in graph[i]:
            for k in graph[i][j]:
                #Checking if there is a name attribute of the edge
                if graph[i][j][0].get('name') == None:
                    remove_list.append((i, j))
                    continue
                #Going through the road_list and seeing if any match the name of the edge
                keep = False
                for roads in road_list:
                    if type(graph[i][j][0]['name']) == list and graph[i][j][0]['name'].count(roads) >= 0:
                        keep = True
                    elif graph[i][j][0]['name'] == roads:
                        keep = True
                if keep == False:
                    remove_list.append((i, j))
    while(len(remove_list)>0) :
        a = remove_list.pop()
        if graph[a[0]].get(a[1]) != None:
            graph.remove_edge(a[0], a[1])
    #Removing all isolated vertices of the Graph
    for i in graph:
        if len(graph[i]) == 0:
            remove_list.append(i)
    while(len(remove_list) > 0):
        x = remove_list.pop()
        graph.remove_node(x)
    return graph