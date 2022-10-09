import string
import networkx as nx
import osmnx as ox
import copy
from shapely.geometry import Point, LineString

def convert_to_linestrings(
    graph,
    road_list=None,
):
    """
    Creates a Linestring for each of the roads, or a certain list of roads
    in the graph produced from a graph generater method or a graph truncate 
    method.

    Parameters
    ----------
    graph : Networkx.MultiDiGraph
        input graph
    road_list : string or list
        the names of roads that will be the only ones converted to Linestrings
    
    Returns
    ----------
    a dictionary containing either all roadnames in road_list or the graph as 
    the key, and the Linestring of the road as the value. 
    """
    linestrings = {}
    if road_list.isinstance(string):
        road = _isolate_road(graph, road_list)
        endpoints = find_end_nodes(graph)
        edge_list = ox.distance.shortest_path(graph, endpoints[0], endpoints[-1], weight='length')
        size = _road_polyline_length(graph, endpoints, edge_list)
        polylines = _generate_road_polyline(graph, endpoints, edge_list, size)
        linestrings[road_list] = polylines
    elif road_list.isinstance(list):
        for road in road_list:
            isolated = _isolate_road(graph, road)
            endpoints = find_end_nodes(isolated)
            edge_list = ox.distance.shortest_path(isolated, endpoints[0], endpoints[-1], weight='length')
            size = _road_polyline_length(isolated, endpoints, edge_list)
            polylines = _generate_road_polyline(isolated, endpoints, edge_list, size)
            linestrings[road] = polylines
    else:
        road_list = _find_roads(graph)
        for road in road_list:
            isolated = _isolate_road(graph, road)
            endpoints = find_end_nodes(isolated)
            edge_list = ox.distance.shortest_path(isolated, endpoints[0], endpoints[-1], weight='length')
            size = _road_polyline_length(isolated, endpoints, edge_list)
            polylines = _generate_road_polyline(isolated, endpoints, edge_list, size)
            linestrings[road] = polylines
    return linestrings
    

def find_end_nodes(graph):
    """
    Find all the nodes in an osmnx graph that are endnodes from the _is_endpoint
    function in the osmnx library

    :param graph: This is the graph where the endpoints to be found are in.
    :return: A list of node ids of the endpoint nodes.
    """
    endNodes = []
    for i in graph:
        if ox.simplification._is_endpoint(graph, i):
            endNodes.append(i)
    return endNodes

def _road_polyline_length(graph, endpoints, edge_list):
    """ 
    Finds how many points are in the LineString that is the road.

    :param graph: The osmnx graph that is being analyzed and has already 
        had isolateRoad called on it
    :param endpoints: The list of endpoints in Graph founded with the function
        findEndNodes
    :param edge_list: The path between the furthes end points in the graph
    :return: a count of the number of points within the LineString that is the road
    """
    count = 0
    NodeTracker = endpoints[0]
    for i in edge_list:
        if i == endpoints[0]:
            continue
        for j in graph[NodeTracker]:
            if i == j:
                if graph[NodeTracker][j][0].get('geometry') != None:
                    for k in graph[NodeTracker][j][0]['geometry'].coords:
                        if k == (graph.nodes[j]['x'], graph.nodes[j]['y']):
                            break
                        count += 1
                else:
                    count += 1
                NodeTracker = j
    return count

def _generate_road_polyline(graph, endpoints, edge_list, size):
    road = [None] * size
    NodeTracker = endpoints[0]
    index = 0
    for i in edge_list:
        if i == endpoints[0]:
            continue
        for j in graph[NodeTracker]:
            if i == j:
                if graph[NodeTracker][j][0].get('geometry') != None:
                    for k in graph[NodeTracker][j][0]['geometry'].coords:
                        if k == (graph.nodes[j]['x'], graph.nodes[j]['y']):
                            break
                        road[index] = k
                        index += 1
                else:
                    road[index] = (graph.nodes[NodeTracker]['x'], graph.nodes[NodeTracker]['y'])
                    index += 1
                NodeTracker = j
    return LineString(road)

def _find_roads(graph):
    """
    Create a list of all the roads in the system.

    :param graph: networkx.MultiDiGraph input graph
    :returns: a list of the roads in the graph
    """
    road_list = []
    for i in graph:
        for j in graph[i]:
            for k in graph[i][j]:
                if k[0].get('name') == None:
                    continue
                elif k[0]['name'].isinstance(string) and road_list.count(k[0]['name']) == 0:
                    road_list.append(k[0]['name'])
    return road_list

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
    cgraph = copy.deepcopy(graph)
    #Removing all the edges in the graph that do not have edges that contain the road name
    for i in cgraph:
        for j in cgraph[i]:
            for k in cgraph[i][j]:
                if cgraph[i][j][0].get('name') == None:
                    nodeRemover.append((i, j))
                    continue
                elif type(cgraph[i][j][0]['name']) == list and cgraph[i][j][0]['name'].count(road) == 0:
                    nodeRemover.append((i, j))
                elif cgraph[i][j][0]['name'] != road:
                    nodeRemover.append((i, j))
    while(len(nodeRemover)>0) :
        a = nodeRemover.pop()
        if cgraph[a[0]].get(a[1]) != None:
            cgraph.remove_edge(a[0], a[1])
    #Removing all isolated vertices of the Graph
    for i in cgraph:
        if len(cgraph[i]) == 0:
            nodeRemover.append(i)
    while(len(nodeRemover) > 0):
        x = nodeRemover.pop()
        cgraph.remove_node(x)
    return cgraph