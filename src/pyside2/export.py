import sys, openpyxl
from openpyxl import Workbook, load_workbook
from pathlib import Path
from array import *

# Writes data to an excel file.
# file_path: Path object designating the worksheet in which
#   the data will be written. Will create the worksheet
#   if it does not exist, and overwrite the data otherwise.
# rows: 2-dimensional indexed collection (such as a list of lists,
#   or tuple of tuples). Each element in the outer collection will
#   be read as a row to be written to the worksheet.
def export_to_excel(file_path, rows):
    # convert Path to string
    file_path = str(file_path)

    # initialize workbook
    wb = Workbook()
    ws = wb.active

    # write rows
    for row in rows:
        ws.append(row)
    
    # save workbook
    wb.save(filename = file_path)