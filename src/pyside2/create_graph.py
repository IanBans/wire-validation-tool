from igraph import *
from openpyxl import *
from pathlib import Path
from report import Report
# Adds data from a fuse map to a graph. Assumes that the first row is
#   a header, and all others contain pin data. Graph must not be empty.
# g: Graph to add vertices to.
# wb_path: Path object pointing to workbook containing fuse map.
# conn_col: Letter of column containing connector information.
# pin_col: Letter of column conatining pin information.
# fuse_col: Letter of column containing fuse rating.
def add_pdc(g, fusemap):

    for row in fusemap:
        #get vertex information
        vconn = row['CONNECTOR'][0]
        vpin = row['CONNECTOR'][1]
        vname = vconn + "|" + vpin
        vfuse = int(row["FUSE"])
        #if vertex doesn't exist, create it
        if len(g.vs.select(name=vname)) == 0:
            g.add_vertex(name=vname, connector=vconn, pin=vpin, fuse_rating=vfuse)
        else: #if vertex exists, update fuse rating
            g.vs.find(name=vname).update_attributes({'fuse_rating':vfuse})
    print('added  pdc to graph')

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
def add_report(g, report):

    contents = report.sheet_list

    for row in contents:
        f_tup = row["FROM"]
        t_tup = row["TO"]
        desc = row["DESC"]
        ecsa = row["CSA"]

        #get vertex information
        fconn = f_tup[0]
        fpin = str(f_tup[1])
        fname = fconn + "|" + fpin
        tconn = str(t_tup[0])
        tpin = str(t_tup[1])
        tname = tconn + "|" + tpin

        #create vertices that don't exist
        if len(g.vs) == 0:
            g.add_vertex(name=fname, connector=fconn, pin=fpin, fuse_rating=0.0)
        elif len(g.vs.select(name=fname)) == 0:
            g.add_vertex(name=fname, connector=fconn, pin=fpin, fuse_rating=0.0)
        if len(g.vs.select(name=tname)) == 0:
            g.add_vertex(name=tname, connector=tconn, pin=tpin, fuse_rating=0.0)

        #create edge
        g.add_edge(fname, tname, wire=desc, csa=ecsa)
    print('added ', report.filename, ' to graph')
