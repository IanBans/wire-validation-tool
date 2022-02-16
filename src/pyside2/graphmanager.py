import networkx as nx
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
