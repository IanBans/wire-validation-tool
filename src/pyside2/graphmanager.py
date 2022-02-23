import networkx as nx
import math
'''
   GraphManager: Class to handle graph operations, reading, writing, traversal
   Fields:
    graph: The networkx graph on which to perform operations
   Methods:
    addPDC(pdc_list): adds the specified PDC list to the graph and updates fuse rating
    addReport(): adds the specified report object to the graph, creating edges between from
        and to (component, pin) combinations
    with attributes
'''
class GraphManager:

    def __init__(self):
        self.g = nx.Graph()


    # addPDC(pdc_list)
    # pdc_list: list of dictionaries of pdc returned from InputParser.readPDC()
    # Adds data from a fuse map list to the graph.
    # updates fuse_rating attribute if nodes already exist
    def addPDC(self, pdc_list):

        for row in pdc_list:
            #get vertex information
            vconn = row['CONNECTOR'][0]
            vpin = row['CONNECTOR'][1]
            vname = vconn + "|" + vpin
            vfuse = int(row["FUSE"])
            # if vertex doesn't exist, create it
            if vname not in self.g:
                self.g.add_node(vname, connector=vconn, pin=vpin, fuse_rating=vfuse)
            # if vertex exists, update fuse rating
            else:
                self.g.nodes[vname]['fuse_rating'] = vfuse

        print('added  pdc to graph')

    # addReport(report)
    # report: report object to add (from InputParser.readReport())
    # Adds nodes from a wire report object to the graph. Graph cannot be empty.
    # adds wires between nodes in the report, updating wire csa and wire description
    def addReport(self, report):

        contents = report.getContents()

        for row in contents:
            f_tup = row["FROM"]
            t_tup = row["TO"]
            wire_desc = row["DESC"]
            wire_csa = row["CSA"]
            # get vertex information
            fconn = str(f_tup[0])
            fpin = str(f_tup[1])
            fname = fconn + "|" + fpin
            tconn = str(t_tup[0])
            tpin = str(t_tup[1])
            tname = tconn + "|" + tpin

            # create vertices that don't exist
            if fname not in self.g:
                self.g.add_node(fname, connector=fconn, pin=fpin, fuse_rating=-1)
            if tname not in self.g:
                self.g.add_node(tname, connector=tconn, pin=tpin, fuse_rating=-1)

            # create wire between the two components
            self.g.add_edge(fname, tname, wire=wire_desc, csa=wire_csa)

        print('added ', report.filename, ' to graph')

    # Traces each wire in the graph from the PDC to its endpoint.
    # Returns a list of 3-tuples, where each tuple represents a wire.
    # The first element is the name of the start vertex.
    # The second element is the name of the end vertex.
    # The third element is a dictionary containing the following keys:
    #   min_csa: Float, lowest CSA of any wire segment.
    def traverse(self):
        # check if graph contains cycles
        if nx.cycle_basis(self.g) != []:
            print("ERROR: Graph contains cycle")
            return (-1, -1, -1)
        # call rtraverse on all edges leading out of the PDC
        fr = nx.get_node_attributes(self.g, "fuse_rating")
        tuples = []
        for node in self.g:
            if fr[node] > 0:
                for nbr in self.g[node]:
                    trace = self.rtraverse(node, nbr, node, {'min_csa':math.inf})
                    for wire in trace:
                        tuples += [wire]
        return tuples

    # Recursive subroutine of traverse(). Should not be called directly.
    # startnode: The first node in the wire.
    # currnode: The node added by the calling method.
    # lastnode: The node added prior to currnode.
    # data: Dictionary of information to report. Key structure is in the comment for traverse().
    def rtraverse(self, startnode, currnode, lastnode, data):
        output = []
        # update data with wire from lastnode to currnode
        if self.g[lastnode][currnode]["csa"] < data["min_csa"]:
            data["min_csa"] = self.g[lastnode][currnode]["csa"]
        # recursively traverse to all neighbors other than lastnode
        for nbr in self.g[currnode]:
            if nbr != lastnode:
                trace = self.rtraverse(startnode, nbr, currnode, data)
                for wire in trace:
                    output += [wire]
        # check if this is the end of the wire
        if output == []:
            output = [(startnode, currnode, data)]
        
        return output

    # Removes all vertices which are part of a cycle.
    def removeCycles(self):
        for list in nx.cycle_basis(self.g):
            self.g.remove_nodes_from(list)

    # For each cycle, counts the number of vertices with more than 2 edges.
    # In other words, finds the number of junctions connecting the cycle to the rest of the graph.
    def analyzeCycles(self):
        output = []
        for list in nx.cycle_basis(self.g):
            count = 0
            for node in list:
                if len(self.g[node]) > 2:
                    count += 1
            output += [count]
        return output
