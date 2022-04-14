import csv
import os
from report import Report


class InputParser:
    """
       InputParser: Functions to parse and store data from files
       Fields:
        reports: a list of previously parsed report Objects
        pdcs: a dict of previously parsed PDC map lists, with filename keys
        heatdata: a dict of previously parsed heat tables, with filename keys
       Methods:
        readPDC(filename)
            reads the pdc file specified at filename and inserts it into pdcs
            filename must be unique to other pdc files
        readReport(filename, from_labels, to_labels, csa, desc)
            reads the report specified at filename with the
            column labels
        readHeatData(filename[, firstRow, firstCol])
            reads the heat table specified at filename and inserts it into heatdata
            filename must be unique to other heat data files
    """

    def __init__(self):
        self._reports = []
        self._pdcs = {}
        self._heatdata = {}

    def getReports(self):
        """
            getter for reports
        """
        return self._reports

    def getPDCs(self):
        """
            getter for pdc list
        """
        return self._pdcs

    def readPDC(self, filename):
        """
            filename: full file path of pdc file
            Reads the PDC fuse map CSV and returns a list of dictionaries
            Each element in the list is a row of the PDC file, in dict format
            {CONNECTOR: (component,pin), FUSE:fuse rating}
        """
        if filename:
            contents_list = []
            with open(filename, mode='rt') as csv_file:
                pdc_dict = csv.DictReader(csv_file, delimiter=',')
                print("Successfully opened pdc fuse map..")
                name = os.path.basename(filename)
                for line in pdc_dict:
                    contents = {}
                    contents["CONNECTOR"] = (line["CONNECTOR"], line["PIN"])
                    contents["FUSE"] = line["FUSE RATING"]
                    contents_list.append(contents)
                if name not in self._pdcs:
                    self._pdcs[name] = contents_list
                return contents_list

        else:
            print("invalid filename passed to readPDC...")
            return []

    def readReport(self, filename, from_labels, to_labels, csa, desc):
        """
            filename: full file path of report file
            (from_conn, from_pin): a tuple of strings - the column names for FROM connector and pin
            (to_conn, to_pin) - a tuple of strings - the column names for TO connector and pin
            csa - string column name for wire CSA
            description - string column name for wire description
            wrapper function for Report class providing storage to the inputparser object
            creates and reads the report, stores the report object in
            self.reports list, and returns the data
        """
        report = Report(filename, from_labels, to_labels, csa, desc)
        self._reports.append(report)
        return report
    
    def readHeatData(self, filename, firstRow=1, firstCol=1):
        """
            filename: full file path of heat table
            firstRow: the index of the row containing amperage values, defaults to row 2
            firstCol: the index of the column containing CSA values, defaults to column 2
            reads the heat table into a dict of dicts, stores it in self.heatdata, and returns it
            the last column of the heat table should contain the ambient temperature
            the outer dict is keyed by wire CSA, and the inner dict is keyed by amperage
        """
        if filename:
            outer = {}
            with open(filename, mode='rt') as csv_file:
                csv_reader = csv.reader(csv_file, skipinitialspace=True)
                while firstRow > 0: # remove extra rows
                    csv_reader.__next__()
                    firstRow = firstRow - 1
                amps = csv_reader.__next__()[firstCol+1:] # amperage values to key inner dict
                cols = [] #cols is defined with the first data row instead of the amperage row,
                coldef = 0 #so it doesn't matter whether the ambient temperature column has a header or not
                for row in csv_reader:
                    row = row[firstCol:] # remove extra columns
                    if coldef == 0:
                        coldef = 1
                        cols = range(1,len(row)-1)
                    inner = {}
                    ambient = float(row[len(row)-1])
                    for i in cols:
                        inner[float(amps[i-1])] = float(row[i]) - ambient
                    outer[float(row[0])] = inner
            name = os.path.basename(filename)
            if name not in self._heatdata:
                self._heatdata[name] = outer
            return outer
            
        else:
            print("invalid filename passed to readHeatData...")
            return {}
