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

    def __init__(self, gui):
        self._g = nx.Graph()
        self.gui = gui

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

        print('added pdc to graph')

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
            # ignore the pin for splice entries
            if fconn[0] != 'S':
                fname = fconn + "|" + fpin
            else:
                fname = fconn
            if tconn[0] != 'S':
                tname = tconn + "|" + tpin
            else:
                tname = tconn

            # create new vertices with a negative fuse rating
            if fname not in self._g:
                self._g.add_node(fname, connector=fconn, pin=fpin, fuse_rating=-1)
            if tname not in self._g:
                self._g.add_node(tname, connector=tconn, pin=tpin, fuse_rating=-1)
            # create wire between the two components
            self._g.add_edge(fname, tname, wire=wire_desc, csa=wire_csa)
        print('added ', report.filename, ' to graph')

    def reportCycle(self, pdc):
        """
            Arguments:
                pdc: node in the graph to check for cycle
            checks for a cycle within the graph from 'pdc' source.
            if one exists, gets minimum CSA, wires, and splice points.
            returns False if no cycle, or tuple with cycle information
            and the set of wires traversed.
            output format:
            (startComponent|startPin, endComponent|endPin, min_csa, wire1, wire2, ..., wire_n,
            splice1, splice2, etc), set_of_wires
        """
        # tracks the minimum CSA, wire names, and splices
        # across each wire trace
        min_csa = math.inf
        wires = set()
        splice_list = []
        search = True
        # check for a cycle, if no cycle, return False
        try:
            loop = dict(nx.find_cycle(self._g, source=pdc))
        except nx.exception.NetworkXNoCycle:
            return False
        else:
            # transform values to expected list format
            # for consistency with bfs_successors
            for key, value in loop.items():
                nodes_list = []
                if not isinstance(value, list):
                    nodes_list.append(value)
                    loop[key] = nodes_list

            loop_head = list(loop)[0]
            while search:
                for start, ends in loop.items():
                    search = False
                    # each wire, update the minimum CSA and add to
                    # the wires list
                    for end in ends:
                        curr_csa = self._g[start][end]['csa']
                        wname = self._g[start][end]['wire']
                        if wname not in wires:
                            wires.add(wname)
                            if curr_csa < min_csa:
                                min_csa = curr_csa
                            # if a splice is detected, there is potential for more ends
                            # a BFS is needed to record all the wires.
                            # set 'search' flag to update the iterator
                            if end[0] == 'S':
                                splice_list.append(end)
                                loop = loop | dict(nx.bfs_successors(self._g, end))
                                search = True

            return ((loop_head, loop_head, min_csa, ', '.join(wires), ', '.join(splice_list)),
                    wires)

    def traceWires(self):
        """
            Traces each wire in the pdc to it's endpoint(s).
            Outputs the start and end component/pin, each wire, and the
            minimum CSA of all wires in the path
            output format:
            (startComponent|startPin, endComponent|endPin, min_csa, wire1, wire2, ..., wire_n,
            splice1, splice2, etc)
        """
        output = []
        # gather all the pdcs into a list
        pdcs = [x for x, y in self._g.nodes(data=True) if y['fuse_rating'] >= 0]
        # start the path at the first PDC, and initialize the dictionary
        for pdc in pdcs:
            path = {}
            path['start'] = pdc
            path['min_csa'] = math.inf
            path['wires'] = set()
            path['splice'] = set()
            loop_wires = set()
            loop = self.reportCycle(pdc)
            # when there's a loop, temporarily modify the
            # wire set to avoid tracing the same wires twice
            if loop:
                output.append(loop[0])
                path['wires'].update(loop[1])
                loop_wires.update(loop[1])
            search = dict(nx.bfs_successors(self._g, source=pdc))
            if bool(search):
                for start, ends in search.items():
                    # each wire, update the minimum CSA and add to
                    # the wires list
                    for end in ends:
                        curr_csa = self._g[start][end]['csa']
                        wname = self._g[start][end]['wire']
                        if wname not in path['wires']:
                            path['wires'].add(wname)
                            if curr_csa < path['min_csa']:
                                path['min_csa'] = curr_csa
                            # when the wire is not in the list of traversed nodes,
                            # it's an endpoint or a loop
                            if end not in set(search.keys()):
                                path['end'] = end
                                if start[0] == 'S':
                                    path['splice'].add(start)

                                splice_list = list(path['splice'])

                                # remove potential loop wires from the path wire set
                                # before adding to output
                                wire_set = path['wires'].difference(loop_wires)
                                output.append((path['start'], path['end'], path['min_csa'],
                                              ', '.join(wire_set), ', '.join(splice_list)))

        return sorted(output, key=lambda y: y[0])

    def printTraverse(self):
        '''
            Prints the result of traceWires
            to console
            Testing helper function. remove on release
        '''
        for item in self.traceWires():
            print(item)

    def printPdcNodes(self):
        '''
            Prints the DFS of every PDC node in the graph
            Test helper function. remove on release
        '''
        pdcs = [x for x, y in self._g.nodes(data=True) if y['fuse_rating'] >= 0]
        pdcs.sort()
        try:
            for node in pdcs:
                print(node, ':', dict(nx.bfs_successors(self._g, node)))
        except nx.exception.NetworkXNoCycle:
            print('no cycles')
