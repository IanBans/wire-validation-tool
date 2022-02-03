from igraph import *
from openpyxl import *
from pathlib import Path

# Adds data from a fuse map to a graph. Assumes that the first row is
#   a header, and all others contain pin data. Graph must not be empty.
# g: Graph to add vertices to.
# wb_path: Path object pointing to workbook containing fuse map.
# conn_col: Letter of column containing connector information.
# pin_col: Letter of column conatining pin information.
# fuse_col: Letter of column containing fuse rating.
def add_pdc(g, wb_path, conn_col="A", pin_col="B", fuse_col="C"):
    wb = load_workbook(filename=str(wb_path))
    ws = wb.active
    for row in range(2, ws.max_row+1):
        #get vertex information
        vconn = str(ws[conn_col+str(row)].value)
        vpin = str(ws[pin_col+str(row)].value)
        vname = vconn + "|" + vpin
        vfuse = str(ws[fuse_col+str(row)].value)
        #if vertex doesn't exist, create it
        if len(g.vs.select(name=vname)) == 0:
            g.add_vertex(name=vname, connector=vconn, pin=vpin, fuse_rating=vfuse)
        else: #if vertex exists, update fuse rating
            g.vs.find(name=vname).update_attributes({'fuse_rating':vfuse})

# Adds data from a wire report to a graph. Assumes that the first row is
#   a header, and all others contain pin data. Graph must not be empty.
# g: Graph to add data to.
# wb_path: Path object pointing to workbook containing wire report.
# fc_col: Letter of column containing from connector.
# fp_col: Letter of column conatining from pin.
# tc_col: Letter of column containing to connector.
# tp_col: Letter of column conatining to pin.
# wirename_col: Letter of column containing wire name.
# csa_col: Letter of column containing cross-sectional area.
def add_report(g, wb_path, fc_col="C", fp_col="D", tc_col="E", tp_col="F", wirename_col="G", csa_col="H"):
    wb = load_workbook(filename=str(wb_path))
    ws = wb.active
    for row in range(2, ws.max_row+1):

        #get vertex information
        fconn = str(ws[fc_col+str(row)].value)
        fpin = str(ws[fp_col+str(row)].value)
        fname = fconn + "|" + fpin
        tconn = str(ws[tc_col+str(row)].value)
        tpin = str(ws[tp_col+str(row)].value)
        tname = tconn + "|" + tpin

        #create vertices that don't exist
        if len(g.vs.select(name=fname)) == 0:
            g.add_vertex(name=fname, connector=fconn, pin=fpin, fuse_rating=0.0)
        if len(g.vs.select(name=tname)) == 0:
            g.add_vertex(name=tname, connector=tconn, pin=tpin, fuse_rating=0.0)
        
        #get edge information
        ewire = str(ws[wirename_col+str(row)].value)
        ecsa = str(ws[csa_col+str(row)].value)

        #create edge
        g.add_edge(fname, tname, wire=ewire, csa=ecsa)