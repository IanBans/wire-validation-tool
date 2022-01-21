import sys, openpyxl, os, inputparser
from igraph import *
from pathlib import Path
from inputparser import InputParser
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
        self.parser = InputParser()
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



    def openCSVFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"CSV Files (*.csv)", options=options)
        self.csv_path.setText(fileName)
        pdc_data = self.parser.readPDC(fileName)





    def openExcelFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        self.excel_path.setText(fileName)
        if "chass.xlsx" in fileName:
            chass_data = self.parser.readReport(fileName, ("TO", "T_TERM"), ("FROM", "F_TERM"), "WIRE CSA", "DESCRIPTION")



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
