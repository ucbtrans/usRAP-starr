import networkx as nx
import osmnx as ox
from collections import defaultdict
from math import cos, sin, pi

def interpolate_roads(
    roads,
    distance=1000,
):
    """
    Find equidistant points along the a linestring using distance
    calculations that assume that these are coordinates on Earth.

    Parameters
    -------
    roads : dictionary with the road name as the key, and value is a list of list of coordinates that make up the sections of road
    distance : distance between each point in meters

    Returns
    --------
    a dictionary with the road name as key and a list of list of points that is the road segments
    """
    interpolated = defaultdict(list)
    index = 0
    distance_temp = 0
    for i in roads:
        for j in roads[i]:
            for k in j:
                if len(k) == 0:
                    continue
                node = k[0]
                path = []
                index = 0
                while index < len(k)-1:
                    distance_next_point = ox.distance.great_circle_vec(node[0], node[1], k[index+1][0], k[index+1][1])
                    if distance_next_point < distance_temp:
                        distance_temp -= distance_next_point
                        index += 1
                        node = k[index]
                    else:
                        bearing = ox.bearing.calculate_bearing(node[0], node[1], k[index+1][0], k[index+1][1])
                        coord = intermediate_point(node[0], node[1], bearing, distance_temp)
                        path.append((coord, bearing))
                        node = coord
                        distance_temp = distance
            if len(path):
                interpolated[i].append(path)
    return interpolated

def intermediate_point(lat, lon, bearing, distance, radius=6371009):
    """
    Find a point a certain distance away from a given set of coordinates.

    Parameters
    ----------
    lat : the latitude of the starting point
    lon : the longitude of the starting point
    bearing : the angle from the starting point where we will find the other point
    distance : the distance from the starting point where the point will be calculated (default in meters)
    radius : radius of the earth (default in meters)

    Returns
    ---------
    (lat, lon) of the new point
    """
    angular_distance = distance / radius
    delta_lat = angular_distance * cos(bearing * pi / 180) * 180 / pi
    delta_lon = angular_distance * sin(bearing * pi / 180) / cos(lat * pi / 180) * 180 / pi
    return lat + delta_lat, lon + delta_lon
