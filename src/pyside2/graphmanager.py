import math
import networkx as nx


class GraphManager:
    """
        GraphManager: Class to handle graph operations, reading, writing, traversal
        Fields:
            _g: The networkx graph on which to perform operations
        Methods:
            addPDC(pdc_list): adds the specified PDC list to the graph and updates fuse rating
            addReport(): adds the specified report object to the graph, creating edges between from
                and to (component, pin) combinations
                with attributes
            printNodes():
                prints all the nodes currently in the graph
            printEdges:
                prints all edges currently in the graph
    """

    def __init__(self):
        self._g = nx.Graph()

    def printNodes(self):
        """
            prints all nodes in the graph, one per line
        """
        for node in list(self._g.nodes.data()):
            print(node)

    def printEdges(self):
        """
            prints all edges in the graph, one per line
        """
        for edge in list(self._g.edges.data()):
            print(edge)

    def addPDC(self, pdc_list):
        """
            pdc_list: list of dictionaries of pdc returned from InputParser.readPDC()
            Adds data from a fuse map list to the graph.
            updates fuse_rating attribute if nodes already exist
        """
        for row in pdc_list:
            # get vertex information
            vconn = row['CONNECTOR'][0]
            vpin = row['CONNECTOR'][1]
            vname = vconn + "|" + vpin
            vfuse = int(row["FUSE"])
            # if vertex doesn't exist, create it
            if vname not in self._g:
                self._g.add_node(vname, connector=vconn, pin=vpin, fuse_rating=vfuse)
            # if vertex exists, update fuse rating
            else:
                self._g.nodes[vname]['fuse_rating'] = vfuse

        print('added  pdc to graph')

    def addReport(self, report):
        """
            report: report object to add (from InputParser.readReport())
            Adds nodes from a wire report object to the graph. Graph cannot be empty.
            adds wires between nodes in the report, updating wire csa and wire description
        """
        contents = report.getContents()

        for row in contents:
            f_tup = row["FROM"]
            t_tup = row["TO"]
            wire_desc = row["DESC"]
            wire_csa = row["CSA"]
            # get vertex information
            fconn = str(f_tup[0])
            fpin = str(f_tup[1])
            tconn = str(t_tup[0])
            tpin = str(t_tup[1])
            if(fconn[0] != 'S'):
                fname = fconn + "|" + fpin
            else:
                fname = fconn
            if(tconn[0] != 'S'):
                tname = tconn + "|" + tpin
            else:
                tname = tconn

            # create vertices that don't exist
            if fname not in self._g:
                self._g.add_node(fname, connector=fconn, pin=fpin, fuse_rating=-1)
            if tname not in self._g:
                self._g.add_node(tname, connector=tconn, pin=tpin, fuse_rating=-1)
            # create wire between the two components
            self._g.add_edge(fname, tname, wire=wire_desc, csa=wire_csa)
        print('added ', report.filename, ' to graph')

    def traverse(self):
        """
            Traces each wire in the graph from the PDC to its endpoint.
            Returns a list of 3-tuples, where each tuple represents a wire.
            The first element is the name of the start vertex.
            The second element is the name of the end vertex.
            The third element is a dictionary containing the following keys:
              min_csa: Float, lowest CSA of any wire segment.
        """
        fuse_rating = nx.get_node_attributes(self._g, "fuse_rating")
        tuples = []
        for node in self._g:
            if fuse_rating[node] > 0:
                for nbr in self._g[node]:
                    trace = self.rtraverse(node, nbr, node, {'min_csa': math.inf})
                    for wire in trace:
                        tuples += [wire]
        return tuples

    def rtraverse(self, startnode, currnode, lastnode, data):
        """
            Recursive subroutine of traverse(). Should not be called directly.
                startnode: The first node in the wire.
                currnode: The node added by the calling method.
                lastnode: The node added prior to currnode.
                data: Dictionary of information to report.
            Key structure is in the comment for traverse().
            TODO: Add loop handling without loop removal.
        """
        output = []
        # update data with wire from lastnode to currnode
        if self._g[lastnode][currnode]["csa"] < data["min_csa"]:
            data["min_csa"] = self._g[lastnode][currnode]["csa"]
        # recursively traverse to all neighbors other than lastnode
        for nbr in self._g[currnode]:
            if nbr != lastnode:
                trace = self.rtraverse(startnode, nbr, currnode, data)
                for wire in trace:
                    output += [wire]
        # check if this is the end of the wire
        if not output:
            output = [(startnode, currnode, data["min_csa"])]

        return output

    def removeCycles(self):
        """
            Removes all vertices in the graph which are part of a cycle.
        """
        pdcs = [x for x,y in self._g.nodes(data=True) if y['fuse_rating']>=0]
        for cycle in nx.cycle_basis(self._g):
            output = []
            for node in cycle:
                if node in pdcs:
                    print('removing pdc node')
                    print(cycle)
            self._g.remove_nodes_from(cycle)

    def analyzeCycles(self):
        """
            finds the number of junctions connecting the cycle to the rest of the graph.
            testing helper function. remove on release
        """
        pdcs =  [x for x,y in self._g.nodes(data=True) if y['fuse_rating']>=0]
        output = []
        for cycle in nx.cycle_basis(self._g):
            count = 0
            if(cycle in pdcs):
                print(cycle)
            for node in cycle:
                if len(self._g[node]) > 2:
                    count += 1
            output += [count]
        return output

    def spliceTraverse(self, traversal='dfs'):
        '''
            Arguments:
                traversal: specify either 'dfs' or 'bfs' to use
                either search type. Default depth first, otherwise bfs
            Traces each wire in the pdc to it's endpoint(s).
            Outputs the start and end component/pin, each wire, and the
            minimum CSA of all wires in the path
            Currently doesn't handle loops in data.
            output format:
            (startComponent|startPin, endComponent|endPin, min_csa, wire1, wire2, ..., wire_n,
            splice1, splice2, etc)
        '''
        output = []
        # get all the pdcs into a list
        pdcs =  [x for x,y in self._g.nodes(data=True) if y['fuse_rating']>=0]
        # start the path at the first PDC, and initialize the dictionary
        for pdc in pdcs:
            path = {}
            path['start'] = pdc
            path['min_csa'] = math.inf
            path['wires'] = []
            path['splice'] = set()
            if(traversal == 'dfs'):
                search = nx.dfs_successors(self._g, source=pdc)
            else:
                search = dict(nx.bfs_successors(self._g, source=pdc))
            if bool(search):
                for start, ends in search.items():
                    # each wire, update the minimum CSA and add to
                    # the wires list
                    for end in ends:
                        curr_csa = self._g[start][end]['csa']
                        wname = self._g[start][end]['wire']
                        path['wires'].append(wname)
                        if curr_csa < path['min_csa']:
                            path['min_csa'] = curr_csa
                        # when the wire is not in the list of traversed nodes, its an endpoint
                        # or a loop
                        if end not in set(search.keys()):
                            path['end'] = end
                            if start[0] == 'S' :
                              path['splice'].add(start)
                            spliceList = list(path['splice'])
                            output.append((path['start'], path['end'], path['min_csa'],
                                           ', '.join(path['wires']), ', '.join(list(path['splice']))))

        return sorted(output, key=lambda y: y[0])

    def printTraverse(self):
        '''
            Prints the result of spliceTraverse
            Testing helper function. remove on release
        '''
        for item in self.spliceTraverse():
            print(item)

    def printPdcNodes(self):
        '''
            Prints the DFS of every PDC node in the graph
            Test helper function. remove on release
        '''
        pdcs =  [x for x,y in self._g.nodes(data=True) if y['fuse_rating']>=0]
        pdcs.sort()
        for node in pdcs:
            print(node, ':', nx.dfs_successors(self._g, source=node))
