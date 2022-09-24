import networkx as nx
import osmnx as ox
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
    endpoints = find_end_nodes(graph)
    edge_list = ox.distance.shortest_path(graph, endpoints[0], endpoints[-1], weight='length')
    size = _road_polyline_length(graph, endpoints, edge_list)
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

def find_end_nodes(graph):
    """
    Find all the nodes in an osmnx graph that are endnodes from the _is_endpoint
    function in the osmnx library

    :param Graph: This is the graph where the endpoints to be found are in.
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

    :param Graph: The osmnx graph that is being analyzed and has already 
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

    