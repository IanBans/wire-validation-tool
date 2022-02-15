import sys, openpyxl, os, inputparser
from pathlib import Path
from inputparser import InputParser
from graphmanager import *
from PySide2 import QtWidgets, QtUiTools
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QRect, QFile, QIODevice, QObject
from openpyxl import Workbook, load_workbook

'''
   App: the main UI and entry point for the application
   Fields:
    parser: input parser object to get input from files
    graph: GraphManager instance to store data into.
   Methods:
    setup_ui(): sets the UI structure and elements
'''
class App(QMainWindow):
    # sets up UI and create parser and GraphManager instances
    def __init__(self):
        super().__init__()
        self.parser = InputParser()
        self.graph = GraphManager()
        self.setupUI()

    def setupUI(self):
        #stacked widget is the container that can be swapped out to change pages
        self.stacked_widget = QStackedWidget()

        self.stacked_widget.setMinimumSize(500, 400)
        self.stacked_widget.setWindowTitle("Paccar Wire Validation Tool")

        front_page = QWidget()
        #dictionary that contains all pages for navigation
        self.pages = {"front": front_page}

        #sets up front page
        front_page_layout = QGridLayout()
        self.stacked_widget.addWidget(front_page)
        front_page.setLayout(front_page_layout)
        font = QFont("Helvetica", 20)
        welcome = QLabel("Paccar Wire Validation Tool")
        welcome.setFont(font)
        welcome.setAlignment(Qt.AlignCenter)
        front_page_layout.addWidget(welcome, 0, 0)

        #add button to go to next page
        file_page_1_button = QPushButton("Next")
        file_page_1_button.clicked.connect(lambda : self.gotoPage("file_picker"))
        front_page_layout.addWidget(file_page_1_button, 1, 0)

        self.stacked_widget.show()

        #Qwidget that contains paths of all wire Reports
        self.wire_report_list = QListWidget()

        self.setupFilePage()

    #pages so far: "front", "file_picker", "wire_reports"
    def gotoPage(self, target):

        if target in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[target])

    #setup for picking all wire reports and PDC
    def setupFilePage(self):

        def chooseWireReport():
            next_wire_report_button = QPushButton("Choose Wire Report")
            next_wire_report_button.clicked.connect(lambda : self.openExcelFileDialog(next_wire_report_button))
            path_label = QLabel("File Path")
            left_widget_layout.insertRow(left_widget_layout.rowCount() - 1, next_wire_report_button)

        def choosePDC():
            next_PDC_button = QPushButton("Choose PDC")
            next_PDC_button.clicked.connect(lambda : self.openCSVFileDialog(next_PDC_button))

            right_widget_layout.insertRow(right_widget_layout.rowCount() - 1, next_PDC_button)

        self.wire_report_paths = []
        self.pdc_paths = []

        file_picker_widgets = QWidget()
        file_picker_layout = QGridLayout()

        self.stacked_widget.addWidget(file_picker_widgets)

        file_picker_widgets.setLayout(file_picker_layout)

        left_widget_layout = QFormLayout()
        right_widget_layout = QFormLayout()
        file_picker_layout.addLayout(left_widget_layout, 0, 0)
        file_picker_layout.addLayout(right_widget_layout, 0, 1)

        #left side of page
        wire_button = QPushButton("Choose Wire Report...")
        left_widget_layout.addRow(wire_button)
        wire_button.clicked.connect(lambda: self.openExcelFileDialog(wire_button))
        add_wire_button = QPushButton("add wire report")
        add_wire_button.clicked.connect(chooseWireReport)
        left_widget_layout.addRow(add_wire_button)

        #right side of page
        PDC_button = QPushButton("Choose PDC...")
        right_widget_layout.addRow(PDC_button)
        add_PDC_button = QPushButton("add PDC")
        add_PDC_button.clicked.connect(choosePDC)
        right_widget_layout.addRow(add_PDC_button)
        PDC_button.clicked.connect(lambda : self.openCSVFileDialog(PDC_button))

        #register current page
        self.stacked_widget.addWidget(file_picker_widgets)
        self.pages.update({"file_picker": file_picker_widgets})

        #button to next page
        #the next button is also the trigger to set up the next page since it relies on data collected from this current page
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.setupWireReports)
        next_button.clicked.connect(lambda: self.gotoPage("wire_reports"))
        file_picker_layout.addWidget(next_button, 1, 0)

    #customize column fields page
    def setupWireReports(self):

        def changeWireReport(index):
            fields_selector.setCurrentIndex(index.row())

        #prints all column fields for all wire reports
        def printDict():
            print("num of reports " + str(num_wire_reports))
            for path, combo_list in combo_box_dict.items():
                print(path)
                for box in combo_list:
                    print(box.currentText())

        #send files to input parser
        for path in self.pdc_paths:
            self.parser.readPDC(path)


        #create a new dictionary from combobox_dict where it is populated by strings instead of combobox objects
        def makeDict():
            for key, value in combo_box_dict.items():
                list = []
                for box in value:
                    list.append(box.currentText())
                self.wire_report_dict.update({key : list})

        # send reports to input Parser
        # & print current graph data
        def sendReports():
            for path, fields in self.wire_report_dict.items():
                from_tuple = (fields[0], fields[1])
                to_tuple = (fields[2], fields[3])
                self.parser.readReport(path, from_tuple, to_tuple, fields[4], fields[5])
                for pdc in self.parser.pdcs.values():
                    self.graph.addPDC(pdc)
                for report in self.parser.reports:
                    self.graph.addReport(report)


                for node in list(self.graph.g.nodes.data()):
                    print(node)
                for edge in list(self.graph.g.edges.data()):
                    print(edge)


        self.wire_report_list.itemClicked.connect(lambda: changeWireReport(self.wire_report_list.currentIndex()))
        num_wire_reports = len(self.wire_report_paths)

        #this list contains all the column fields names.
        fields_list = ["From Component", "From Pin",  "To Component", "To Pin", "Wire CSA", "Description"]


        page = QWidget()
        page_layout = QGridLayout()
        page.setLayout(page_layout)

        self.stacked_widget.addWidget(page)
        self.pages.update({"wire_reports": page})


        page_layout.addWidget(self.wire_report_list, 0, 0)
        fields_selector = QStackedWidget()
        page_layout.addWidget(fields_selector, 0, 1)


        #the Dictionary that contains all the wire columnn fields. The key is the wire path and the value is a list of QComboBoxes thatt contain wire fields
        combo_box_dict = {}
        #the real dictionary that has the same data as the above dict but stores the data as a list of strings instead of a list of QWidgets
        self.wire_report_dict = {}


        #create combo boxes and add them to page
        for wire_report in self.wire_report_paths:

            fields_layout = QFormLayout()
            fields_container = QWidget()
            fields_container.setLayout(fields_layout)
            combo_box_list = []
            combo_box_dict.update({wire_report : combo_box_list})
            column_names = self.parser.readColumnNames(wire_report)

            for i in range(len(fields_list)):
                combo_box = QComboBox()
                combo_box.addItem("Choose Option")
                for name in column_names:
                    combo_box.addItem(name)

                label = QLabel(fields_list[i])
                combo_box_list.append(combo_box)
                combo_box.setCurrentIndex(0)
                fields_layout.addRow(combo_box, label)

            fields_selector.addWidget(fields_container)

        fields_selector.setCurrentIndex(0)


        submit = QPushButton("Submit")
        page_layout.addWidget(submit, 2, 0)
        submit.clicked.connect(makeDict)
        submit.clicked.connect(sendReports)

    def openCSVFileDialog(self, button):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"CSV Files (*.csv)", options=options)
        self.pdc_paths.append(fileName)
        if fileName:
            button.setText(fileName)

    def openExcelFileDialog(self, button):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        #save data for gui to use later
        self.wire_report_paths.append(fileName)
        self.wire_report_list.addItem(fileName)
        if fileName:
            button.setText(fileName)

    # Currently Unused
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
    window = App()
    sys.exit(app.exec_())
