from inputparser import *
from graphmanager import *

i = InputParser()
g = GraphManager()
r = i.readReport("C:\\Users\\Ian\\Documents\\test\\wire_report.xlsx", ("From Component: Name", "From Pin/Cavity: Name"), ("To Component: Name", "To Pin/Cavity: Name"), "Wire CSA", "Name")
eng = i.readReport("C:\\Users\\Ian\\Documents\\test\\eng - Copy.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
roof = i.readReport("C:\\Users\\Ian\\Documents\\test\\roof - Copy.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
chass = i.readReport("C:\\Users\\Ian\\Documents\\test\\chass.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
g.addReport(r)
g.addReport(chass)
g.addReport(roof)
g.addReport(eng)
p = i.readPDC("C:\\Users\\Ian\\Documents\\test\\PDCfuseMap.csv")
g.addPDC(p)
#g.removeCycles()
g.printPdcNodes()
