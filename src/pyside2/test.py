from inputparser import *
from graphmanager import *
from export import *

i = InputParser()
g = GraphManager()
e = ExportManager()
r = i.readReport("C:\\Users\\Ian\\Documents\\test\\wire_report.xlsx", ("From Component: Name", "From Pin/Cavity: Name"), ("To Component: Name", "To Pin/Cavity: Name"), "Wire CSA", "Name")
#g.addReport(r)
eng = i.readReport("C:\\Users\\Ian\\Documents\\test\\eng - Copy.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
roof = i.readReport("C:\\Users\\Ian\\Documents\\test\\roof - Copy.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
chass = i.readReport("C:\\Users\\Ian\\Documents\\test\\chass.xlsx", ("FROM", "F_TERM"), ("TO", "T_TERM"), "WIRE CSA", "CIRCUIT NUMBER")
t1report = i.readReport("C:\\Users\\Ian\\Documents\\test\\allInOneCsv_t1.xlsx", ("From Component: Name", "From Pin/Cavity: Name"), ("To Component: Name", "To Pin/Cavity: Name"), "Wire CSA", "Name")
t2report = i.readReport("C:\\Users\\Ian\\Documents\\test\\allInOneCsv_T2.xlsx", ("From Component: Name", "From Pin/Cavity: Name"), ("To Component: Name", "To Pin/Cavity: Name"), "Wire CSA", "Name")

g.addReport(t1report)
#g.addReport(t2report)
#g.addReport(eng)
e.setFilePath("C:\\Users\\Ian\\Documents\\test\\output_t1_bfs.xlsx")
p = i.readPDC("C:\\Users\\Ian\\Documents\\test\\PDCfuseMap.csv")
t1pdc = i.readPDC("C:\\Users\\Ian\\Documents\\test\\pdc outs t1.csv")
t2pdc = i.readPDC("C:\\Users\\Ian\\Documents\\test\\pdc outs t2.csv")
g.addPDC(t1pdc)
#g.addPDC(t2pdc)
g.analyzeCycles()
e.exportToExcel(g.spliceTraverse('bfs'))
g.printPdcNodes()
