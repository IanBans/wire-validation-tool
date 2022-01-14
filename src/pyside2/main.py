import sys, openpyxl, csv, os
from igraph import *
from pathlib import Path
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
            #reads the PDC from the supplied file
            with open(fileName, mode='r') as csv_file:
                pdcDict = csv.DictReader(csv_file, delimiter=',')
                #print(list(pdcDict))
                print("Successfully opened pdc fuse map..")
                return list(pdcDict)
        else:
            print("invalid filename passed to readPDC")



    def openExcelFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        self.readWireMap(self.fileName)

    def readWireMap(self, fileName):
        def wire_pin_convert(lst):
            for i in range(0, len(lst), 2):
                res_dct = {COMPONENT: lst[i], PIN: lst[i+1], FUSE_RATING: 0}
            return res_dict

        if fileName:
            self.excel_path.setText(fileName)
            wb = load_workbook(filename=fileName)
            sheet = wb.active
            for col in sheet.iter_cols(min_col=3, max_col=6, min_row=1, max_row=sheet.max_row, values_only=True):
                print(wire_pin_convert(col))


    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"choose files", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        if files:
            for file in files:
                print(file)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"choose file to save",Path.home().as_posix(),"All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App("basic_input.ui")
    sys.exit(app.exec_())
