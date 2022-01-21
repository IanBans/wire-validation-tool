import openpyxl, os, sys
from openpyxl import Workbook, load_workbook
'''
   Report: modeling a single excel wire report file
   Properties:
   fileName: the name of the report file
   toLabels: a tuple of strings containing the column labels of TO (component, pin)
   fromLabels: a tuple of strings containing the column labels of FROM (component, pin)
   sheet_list: a list output of the report contents in
    {FCOMP, FPIN, TCOMP, TPIN, CSA, DESC} dictionary format
'''
class Report:

    def __init__(self, filename, from_labels, to_labels, csa, desc):
        self.filename = filename
        self.to_labels = to_labels
        self.from_labels = from_labels
        self.csa = csa
        self.desc = desc
        self.sheet_list = []
        print(self.filename)
        self.read()

    def read(self):

        #maps column names to column numbers for identification
        def mapColumnNames(report):
            names = {}
            num = 0
            for col in report.iter_cols(1, report.max_column, 1, 1, True):
                names[col[0]] = num
                num = num + 1
            return names


        if self.filename:
            wb = load_workbook(filename=self.filename)
            sheet = wb.active
            column_map = mapColumnNames(sheet)
            try:
                for row in sheet.iter_rows(2, sheet.max_row, values_only=True):
                    dict = {}
                    if(row[0] != None):
                        dict["FCOMP"] = row[column_map[self.from_labels[0]]]
                        dict["FPIN"] = row[column_map[self.from_labels[1]]]
                        dict["TCOMP"] = row[column_map[self.to_labels[0]]]
                        dict["TPIN"] = row[column_map[self.to_labels[1]]]
                        dict["CSA"] = row[column_map[self.csa]]
                        dict["DESC"] = row[column_map[self.desc]]
                        self.sheet_list.append(dict)
                return self.sheet_list
            except KeyError as e:
                print("check column label " + str(e) + " matches file")
        else:
            print("bad filename in Report.read")
