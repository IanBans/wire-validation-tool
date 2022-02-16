from inputparser import *
from graphmanager import *
import networkx as nx

i = InputParser()
g = GraphManager()
r = i.readReport("wire_report.xlsx", ("From Component: Name", "From Pin/Cavity: Name"), ("To Component: Name", "To Pin/Cavity: Name"), "Wire CSA", "Name")
g.addReport(r)
p = i.readPDC("PDCfuseMap.csv")
g.addPDC(p)
#g.removeCycles()
#print(nx.cycle_basis(g.g))
#print(g.traverse())
print(g.analyzeCycles())
