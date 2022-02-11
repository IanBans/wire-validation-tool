import openpyxl, os
from openpyxl import Workbook, load_workbook
'''
   Report: modeling a single excel wire report file
   Author: Ian Bansenauer
   Properties:
   filepath: the path of the report file
   filename: the name of the original file
   toLabels: a tuple of strings containing the column labels of TO (component, pin)
   fromLabels: a tuple of strings containing the column labels of FROM (component, pin)
   sheet_list: a list output of the report contents in
    {FROM: (component, pin), TO: (component, pin) CSA:int, DESC:str} dictionary format
    read(): reads the report stored in filepath and adds it to sheet_list
'''
class Report:

    def __init__(self, filepath, from_labels, to_labels, csa, desc):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.to_labels = to_labels
        self.from_labels = from_labels
        self.csa = csa
        self.desc = desc
        self.sheet_list = []
        self.read()


    def getContents(self):
        return self.sheet_list

    #reads the report from filepath and stores output in sheet_list, or empty list if
    #reading unsuccessful
    def read(self):

        #maps column names to column numbers for identification
        def mapColumnNames(report):
            names = {}
            for first_row in report.iter_rows(1, 1, 1, sheet.max_column, True):
                row = first_row
            for num in range(0, sheet.max_column):
                    names[row[num]] = num
            return names


        if self.filepath:
            wb = load_workbook(self.filepath, read_only=True)
            sheet = wb.active
            column_map = mapColumnNames(sheet)
            #creates a list of NoneType to check for empty rows
            empty = [None]*sheet.max_column
            try:
                for row in sheet.iter_rows(2, sheet.max_row, values_only=True):
                    dict = {}
                    row_list = list(row)
                    #if row is empty, don't process it
                    if(row_list != empty):
                        dict["FROM"] = (row[column_map[self.from_labels[0]]], row[column_map[self.from_labels[1]]])
                        dict["TO"] = (row[column_map[self.to_labels[0]]], row[column_map[self.to_labels[1]]])
                        dict["CSA"] = row[column_map[self.csa]]
                        dict["DESC"] = row[column_map[self.desc]]
                        self.sheet_list.append(dict)
                print("successfully read report: ", self.filename)
                return self.sheet_list
            except KeyError as e:
                print("check column label " + str(e) + " matches file")
                return []
        else:
            print("bad filename in Report.read")
