import csv
import os
from report import Report


class InputParser:
    """
       InputParser: Functions to parse and store data from files
       Fields:
        reports: a list of previously parsed report Objects
        pdcs: a dict of previously parsed PDC map lists, with filename keys
       Methods:
        readPDC(filename)
            reads the pdc file specified at filename and inserts it into pdcs
            filename must be unique to other pdc files
        readReport(filename, from_labels, to_labels, csa, desc)
            reads the report specified at filename with the
            column labels
    """

    def __init__(self, gui):
        self._reports = []
        self._pdcs = {}
        self.gui = gui

    def getReports(self):
        """
            getter for reports
        """
        return self._reports
    def clearParsedData(self):
        """
            deletes all cached parsed data
        """
        self._reports.clear()
        self._pdcs.clear()
        print("cleared parser data")

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
                name = os.path.basename(filename)
                for line in pdc_dict:
                    contents = {}
                    contents["CONNECTOR"] = (line["CONNECTOR"], line["PIN"])
                    contents["FUSE"] = line["FUSE RATING"]
                    contents_list.append(contents)
                if name not in self._pdcs:
                    self._pdcs[name] = contents_list
                    print("Successfully read PDC map: ", name)
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
        report = Report(filename, from_labels, to_labels, csa, desc, self.gui)
        self._reports.append(report)
        return report
