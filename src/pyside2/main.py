import sys, openpyxl, csv, os, report
from igraph import *
from pathlib import Path
from report import Report
from PySide2 import QtWidgets, QtUiTools
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QRect, QFile, QIODevice, QObject
from openpyxl import Workbook, load_workbook

class App(QMainWindow):
    #load the ui file and find the elements
    def __init__(self, ui_filename):
        super().__init__()
        ui_file = QFile(ui_filename)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        self.setup_ui()
        self.window.show()

    #find widgets and set the click functions
    def setup_ui(self):
        self.pick_excel = self.window.findChild(QPushButton, 'pick_excel')
        self.pick_csv = self.window.findChild(QPushButton, 'input_csv')
        self.excel_path = self.window.findChild(QLabel, 'excel_path')
        self.csv_path = self.window.findChild(QLabel, 'csv_path')
        self.save_path = self.window.findChild(QPushButton, 'save_path')
        self.pick_csv.clicked.connect(self.openCSVFileDialog)
        self.pick_excel.clicked.connect(self.openExcelFileDialog)


    #opens the file dialog for picking CSV files
    def openCSVFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        csvFileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"CSV Files (*.csv)", options=options)
        self.readPDC(csvFileName)

    #Reads the PDC fuse map CSV and returns a list of the dictionaries
    #Each element in the list is a row of the PDC file, in dict format
    def readPDC(self, fileName):
        if fileName:
            #Sets the GUI path
            self.csv_path.setText(fileName)
            with open(fileName, mode='r') as csv_file:
                pdcDict = csv.DictReader(csv_file, delimiter=',')

                print("Successfully opened pdc fuse map..")
                return list(pdcDict)
        else:
            print("invalid filename passed to readPDC...")


    #opens the file dialog for picking an excel file
    def openExcelFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        wr = Report(fileName, ("FROM", "FROM_TERM"), ("TO", "TO_TERM"), "WIRE_CSA", "DESCRIPTION")
        contents = wr.read()
        self.excel_path.setText(fileName)
        if contents:
            print(contents)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App("basic_input.ui")
    sys.exit(app.exec_())
