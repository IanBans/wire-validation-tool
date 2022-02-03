import igraph

print(igraph.__version__)



def create_graph():
    g = igraph.Graph(directed=True)

    #add vertices
    g.add_vertices(7)

    # Add ids and labels to vertices
    # input will be as dict
    for i in range(len(g.vs)):
        g.vs[i]["id"]= i
        g.vs[i]["label"]= str(i)


    # Add edges
    #g.add_edges([(0,2),(0,1),(0,3),(1,2),(1,3),(2,4),(3,4)])

    # a linear graph 5 vertecies
    #g.add_edges([(0,1),(1,2),(2,3),(3,4)])

    #a graph with splices 7 vertecies
    #g.add_edges([(0,1),(1,2),(2,3),(2,4),(3,5),(4,6)])

    #a graph with splices and a loop
    g.add_edges([(0,1),(1,2),(2,3),(2,4),(3,5),(4,6),(6,2)])

    # Add weights and edge labels (dont think we'll need these.)
    weights = [8,6,3,5,6,4,9]
    g.es['weight'] = weights
    g.es['label'] = weights


    #print info
    print("Number of vertices in the graph:", g.vcount())
    print("Number of edges in the graph", g.ecount())
    print("Is the graph directed:", g.is_directed())
    print("Maximum degree in the graph:", g.maxdegree())
    print("Adjacency matrix:\n", g.get_adjacency())

    #get neighbors of a vertex. modes: in (predecessor), out (successors), all (both)
    #print(g.neighbors(1, mode="out"))
    #print(g.neighbors(2, mode="out"))
    new_list = []
    find_splices(g, 0, new_list)
    print(g.is_loop(edges=None))

    ## workflow: First add number of desired vertices, then add labels and other label information to each vertex.

    #Question: if we only display connections from start to end pin, is the end pin at the splice or does it include multiple end points for each splice?


def find_splices(g, i, tracking_list):
    if(i in tracking_list):
        print("loop detected starting at ", i)
        return
    tracking_list.append(i)
    neighbors = g.neighbors(i, mode="out")
    
    if len(neighbors) > 1:
        print("splice with ", i, "to ", neighbors)
        for x in neighbors:
            find_splices(g, x, tracking_list)
    elif len(neighbors) == 1:
        print(neighbors)
        find_splices(g, neighbors[0], tracking_list)

create_graph()