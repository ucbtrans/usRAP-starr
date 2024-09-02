import networkx as nx
import osmnx as ox
from shapely.geometry import LineString
from collections import defaultdict

def make_road_list(graph):
    """
    Make a graph that only contains 1 road name for road in the system.

    Parameters
    ----------
    graph : Networkx.MultiDiGraph
        input graph

    Returns
    ----------
    dictionary with the key being a road name, and the value is a Netowrkx.Graph
    of all edges with that road name
    """
    roads = set()
    for i in graph:
        for j in graph[i]:
            if graph[i][j][0].get('name') and type(graph[i][j][0].get('name')) == list:
                for k in graph[i][j][0]['name']:
                    roads.add(k)
            elif graph[i][j][0].get('name') and type(graph[i][j][0].get('name')) == str:
                roads.add(graph[i][j][0].get('name'))
    return {i:_isolate_road(graph, i) for i in roads} 

def convert_to_linestrings(
    roads
):
    """
    Creates a Linestring for each of the roads, or a certain list of roads
    in the graph produced from a graph generater method or a graph truncate 
    method. Also finds the intersections at the same time.

    Parameters
    ----------
    roads : a dictionary with road name as key, and Networkx.MultiDiGraph as value
    
    Returns
    ----------
    roadstrings : {roadname : [[[section1, section2]]]}
        a dictionary where the key is the name of the road, and the value is a list of
        all sections of roads for every road with the name given
    intersections : {roadname: [[road1], [road2]]}
        a dictionary where the key is the name of the road, and the value is a list of
        coordinates of each road where there is an intersection
    """
    roadstrings = defaultdict(list)
    intersections = defaultdict(list)
    for i in roads:
        endpoints = find_end_nodes(roads[i])
        while len(endpoints):
            node = endpoints[0]
            visited = set()
            visited.add(node)
            frontier = [(node, None)]
            path = []
            paths = []
            intersection = []
            while len(frontier):
                node, prev = frontier.pop()
                node_found = False
                if len(path) == 0 and prev:
                    path.append((roads[i].nodes[prev]['y'], roads[i].nodes[prev]['x']))
                if prev and roads[i][prev][node][0].get('geometry'):
                    for j, coords in enumerate(roads[i][prev][node][0]['geometry'].coords):
                        if j > 0:
                            path.append((coords[1], coords[0]))
                else:
                    path.append((roads[i].nodes[node]['y'], roads[i].nodes[node]['x']))
                    intersection.append((roads[i].nodes[node]['y'], roads[i].nodes[node]['x']))
                for j in roads[i][node]:
                    if j not in visited:
                        visited.add(j)
                        frontier.append((j, node))
                        node_found = True
                if node_found == False:
                    paths.append(path[:])
                    path = []
            roadstrings[i].append(paths[:])
            intersections[i].append(intersection[:])
            for j in endpoints:
                if j in visited:
                    endpoints.remove(j)
    return roadstrings, intersections
    

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