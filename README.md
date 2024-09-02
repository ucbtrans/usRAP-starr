# usRAP-starr
versions used:
- osmnx - 1.2.1
- networkx - 2.8.5
- Shapely - 1.8.2

At this stage, the goal is to get google street view images of whole road systems to be used to calculate the score. In order to use the google street view API, we need three things.

1. The coordinates of where to take the images
2. The bearing at the coordinates to take the images.
3. The road name to link the image with

Keeping these things in mind, I will go through the process of what is already been done, what needs to be improved, as well as the overall thought process that is in the design.

There is this library called OSMNX that is the API for Open Street Map. This is where we will get the information that will be used in the API calls. This library makes a Netowrkx graph of the road systems of an area. The file that contains the methods for creating these graphs is generate.py and truncate.py. generate.py has a few ways to create graphs based on certain input information (Area query, Lat Lon Box, etc.) and truncate.py has ways to get a smaller Networkx graph from a larger graph.

As a side note, the Networkx data structure that OSMNX makes is that of an adjacency list that is a dictionary of dictionary of dictionary of dictionaries. An example of this is {node_id : {neighbor_id : {0 : {edge attributes}}}}. There are a lot of attributes the only ones needed are 'name' and 'geometry'. 'name' is a string of the street that is the edge, and 'geometry' is a Linestring of coordinates that keeps track of curvature between two nodes.

Now that we have a working graph, we need to isolate each of the roads in the system so that we can get the road geometry and tie it to the roadname. That is what the make_road_list() is for. Essentially, what it does is make a copy of the graph, and removes all edges that does not have the road name that we want. It does this for all roads in the system, and the output is a dictionary with the format being {road_name : road_graph}.

The next step is to get the coordinates in two ways.

1. Get all the intersections of that road
2. Get evenly distanced points on that road

Once we have the graph of only one road, we can then get the geometry of that road. The method that does this is convert_to_linestrings. There is a reason why I chose to do it in the way that I did, so I will start with the context. The road name is not a key, so it is possible that there are two streets with the same name, and this is especially true if you are going to be looking at all roads in a county, state, or any area with multiple cities. I call this the Main Street Dilemma.

Knowing this issue, the way I chose to go about this is to start by getting all endpoints in the graph. Road geometries can be unpredictable so we cannot assume that each road has two ends. That is why I chose to do a DFS algorithm starting at one of the enpoints. As we explore the graph, we keep track of the path taken. If there is any backtracking, we start another path and keep going. After the DFS algorithm finishes, we remove all the endnodes that were visited, and we repeat the algorithm from a new endpoint if there are any endnodes not visited yet (hence will be a different road with the same name). To keep track of the intersection coordinates with the sections of road, it also makes a data structure that keeps track of the intersections while doing DFS. There are two things that are returned. First is the road geometry which is a dictionary structured as {roadname: [[[section 1], [section 2]]]}. The second is the road intersections structured as {roadname: [[road 1], [road 2]]}. The indexing should be the same between the two structures.

NOTE: The method described above needs to be debugged.

This next section will be using the structure of road geometries. The method is road_interpolation(). It starts at one end of the coordinate list given, and as it goes through the list, it keeps track of the distance between each point. Once a certain distance has passed, it records the coordinate, and keeps on going. It returns a dictionary of {road_name: [[section 1, section 2]]}.

NOTE: This method's input is not correctly alligned with the output of convert_to_linestrings(). The output of that method is {roadname: [[[section 1], [section 2]]]}, and the input of this method is {road_name: [[section 1, section 2]]}. The input does not account for different roads, but treats each section as its own road.

NOTE2: When running a newer version of OSMNX, the method great_circle_vec was deprecated, and the new name is now great_circle. When looking at both method documentations, it does not seem to be very different, but something to watch out for when running on a different machine.

The actual image extraction is in the early process. The way it is still in the process of making the actual API call.

At this point the next steps will be to:

1. Debug convert_to_linestrings()
2. Align it with interpolate_roads
3. Add bearings to what is returned by convert_to_linestrings() and interpolate_roads()
4. Make the actual API calls and apply it to a dictionary where the value is a list of list of coordinates.

