from igraph import *
from openpyxl import *
from report import Report

'''
   GraphManager: Class to handle graph operations, reading, writing, traversal
   Fields:
    graph: The igraph graph on which to perform operations
   Methods:
    add_pdc(pdc_list): adds the specified PDC list to the graph and updates fuse rating
    add_report(): adds the specified report object to the graph, creating edges between from
        and to (component, pin) combinations
    with attributes
    find_splices(): finds loops in a directed graph. W.I.P.
'''
class GraphManager:

    def __init__(self):
        self.g = Graph()
        #add dummy vertex to avoid errors when adding to empty graph
        self.g.add_vertex(name="dummy")
        self.has_dummy = True


    #addPDC(pdc_list)
    #pdc_list: list of dictionaries of pdc returned from InputParser.readPDC()
    # Adds data from a fuse map list to the graph.
    #updates fuse_rating attribute if nodes already exist
    def addPDC(self, pdc_list):

        for row in pdc_list:
            #get vertex information
            vconn = row['CONNECTOR'][0]
            vpin = row['CONNECTOR'][1]
            vname = vconn + "|" + vpin
            vfuse = int(row["FUSE"])
            #if vertex doesn't exist, create it
            if len(self.g.vs.select(name=vname)) == 0:
                self.g.add_vertex(name=vname, connector=vconn, pin=vpin, fuse_rating=vfuse)
            else: #if vertex exists, update fuse rating
                self.g.vs.find(name=vname).update_attributes({'fuse_rating':vfuse})
        #delete dummy vertex if it exists
        if (self.has_dummy):
            self.g.vs.find(name="dummy").delete()
            self.has_dummy = False
        print('added  pdc to graph')

    #addReport(report)
    #report: report object to add (from InputParser.readReport())
    # Adds nodes from a wire report object to the graph. Graph cannot be empty.
    # adds wires between nodes in the report, updating wire csa and wire description
    def addReport(self, report):

        contents = report.getContents()

        for row in contents:
            f_tup = row["FROM"]
            t_tup = row["TO"]
            desc = row["DESC"]
            ecsa = row["CSA"]

            #get vertex information
            fconn = str(f_tup[0])
            fpin = str(f_tup[1])
            fname = fconn + "|" + fpin
            tconn = str(t_tup[0])
            tpin = str(t_tup[1])
            tname = tconn + "|" + tpin

            #create vertices that don't exist
            if len(self.g.vs) == 0:
                self.g.add_vertex(name=fname, connector=fconn, pin=fpin, fuse_rating=0.0)
            elif len(self.g.vs.select(name=fname)) == 0:
                self.g.add_vertex(name=fname, connector=fconn, pin=fpin, fuse_rating=0.0)
            if len(self.g.vs.select(name=tname)) == 0:
                self.g.add_vertex(name=tname, connector=tconn, pin=tpin, fuse_rating=0.0)

            #create edge between from and to with csa and description
            self.g.add_edge(fname, tname, wire=desc, csa=ecsa)

        print('added ', report.filename, ' to graph')

    #findSplices(report)
    #TODO: only works on directed graphs
    #Work in progress
    def findSplices(self, i=0, tracking_list=[]):
        if(i in tracking_list):
            print("loop detected starting at ", i)
            return
        tracking_list.append(i)
        neighbors = self.g.neighbors(i, mode="out")

        if len(neighbors) > 1:
            print("splice with ", i, "to ", neighbors)
            for x in neighbors:
                self.findSplices(x, tracking_list)
        elif len(neighbors) == 1:
            print(neighbors)
            self.findSplices(neighbors[0], tracking_list)
