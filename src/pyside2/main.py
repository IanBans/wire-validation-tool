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
        #took out the part where we read gui elements from csv
        #ui_file = QFile(ui_filename)
        #ui_file.open(QFile.ReadOnly)
        #loader = QUiLoader()
        #self.window = loader.load(ui_file)
        self.parser = InputParser()


        #ui_file.close()
        self.setup_ui()

    def setup_ui(self):
        #stacked widget is the container that can be swapped out to change pages
        self.stacked_widget = QStackedWidget()

        self.stacked_widget.setMinimumSize(500, 400)
        self.stacked_widget.setWindowTitle("Paccar Wire Validation Tool")


        self.front_page = QWidget()
        #dictionary that contains all pages for navigation
        self.pages = {"front": self.front_page}

        #front page settup. nothing much here
        self.front_page_layout = QGridLayout()
        self.stacked_widget.addWidget(self.front_page)
        self.front_page.setLayout(self.front_page_layout)
        welcome = QLabel("hello world")
        self.front_page_layout.addWidget(welcome, 0, 0)

        #add button to go to nexxt page
        file_page_1_button = QPushButton("Next")
        file_page_1_button.clicked.connect(lambda : self.goto_page("file_picker"))
        self.front_page_layout.addWidget(file_page_1_button, 1, 0)

        self.stacked_widget.show()

        #Qwidget that contains paths of all wire Reports
        self.wire_report_list = QListWidget()

        self.settup_file_page()

    #pages so far: "front", "file_picker", "wire_reports"
    def goto_page(self, target):

        if target in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[target])

    #settup for picking all wire reports and PDC
    def settup_file_page(self):

        def add_wire_report():
            next_wire_report_button = QPushButton("Choose Wire Report")
            next_wire_report_button.clicked.connect(self.openExcelFileDialog)

            path_label = QLabel("File Path")

            self.left_widget_layout.insertRow(self.left_widget_layout.rowCount() - 1, next_wire_report_button)



        def add_PDC():
            next_PDC_button = QPushButton("Choose PDC")
            next_PDC_button.clicked.connect(self.openCSVFileDialog)

            self.right_widget_layout.insertRow(self.right_widget_layout.rowCount() - 1, next_PDC_button)



        self.wire_report_paths = []

        self.pdc_paths = []

        self.file_picker_widgets = QWidget()
        self.file_picker_layout = QGridLayout()
        self.stacked_widget.addWidget(self.file_picker_widgets)

        self.file_picker_widgets.setLayout(self.file_picker_layout)

        self.left_widget_layout = QFormLayout()
        self.right_widget_layout = QFormLayout()
        #left_widget.setLayout(self.left_widget_layout)
        #right_widget.setLayout(right_widget_layout)
        self.file_picker_layout.addLayout(self.left_widget_layout, 0, 0)
        self.file_picker_layout.addLayout(self.right_widget_layout, 0, 1)

        #left side of page
        wire_button = QPushButton("Choose Wire Report...")
        excel_path = QLabel("File Path")
        self.left_widget_layout.addRow(wire_button, excel_path)
        wire_button.clicked.connect(self.openExcelFileDialog)
        self.add_wire_button = QPushButton("add wire report")
        self.add_wire_button.clicked.connect(add_wire_report)
        self.left_widget_layout.addRow(self.add_wire_button)

        #right side of page
        PDC_button = QPushButton("Choose PDC...")
        excel_path = QLabel("File Path")
        self.right_widget_layout.addRow(PDC_button, excel_path)
        self.add_PDC_button = QPushButton("add PDC")
        self.add_PDC_button.clicked.connect(add_PDC)
        self.right_widget_layout.addRow(self.add_PDC_button)
        PDC_button.clicked.connect(self.openCSVFileDialog)

        #register current page
        self.stacked_widget.addWidget(self.file_picker_widgets)
        self.pages.update({"file_picker": self.file_picker_widgets})

        #button to next page
        #the next button is also the trigger to set up the next page since it relies on data collected from this current page
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.setup_wire_reports)
        next_button.clicked.connect(lambda: self.goto_page("wire_reports"))
        self.file_picker_layout.addWidget(next_button, 1, 0)

    #customize column fields page
    #currently saves data to self.model but does not record data properly
    def setup_wire_reports(self):

        def change_wire_report(index):
            fields_selector.setCurrentIndex(index.row())

        #prints all column fields for all wire reports
        def print_dict():

            print("num of reports " + str(num_wire_reports))
            for path, combo_list in combo_box_dict.items():
                print(path)
                for box in combo_list:
                    print(box.currentText())


        #create a new dictionary from combobox_dict where it is populated by strings instead of combobox objects
        def make_dict():
            for key, value in combo_box_dict.items():
                list = []
                for box in value:
                    list.append(box.currentText())
                self.wire_report_dict.update({key : list})

        self.wire_report_list.itemClicked.connect(lambda: change_wire_report(self.wire_report_list.currentIndex()))
        num_wire_reports = len(self.wire_report_paths)

        #this list contains all the column fields names. Currently just a place holder list. first option needs to be junk option
        fields_list = ["Select Option", "From", "Wire", "Pin", "Stuff"]


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
        for wire_report in range(num_wire_reports):

            fields_layout = QFormLayout()
            fields_container = QWidget()
            fields_container.setLayout(fields_layout)
            combo_box_list = []
            combo_box_dict.update({self.wire_report_paths[wire_report] : combo_box_list})

            for i in range(10):
                combo_box = QComboBox()
                for field in fields_list:
                    combo_box.addItem(field)

                label = QLabel("Column Field " + str(i))
                combo_box_list.append(combo_box)
                combo_box.setCurrentIndex(0)
                fields_layout.addRow(combo_box, label)

            fields_selector.addWidget(fields_container)

        fields_selector.setCurrentIndex(0)


        submit = QPushButton("Submit")
        page_layout.addWidget(submit, 2, 0)
        submit.clicked.connect(print_dict)
        submit.clicked.connect(make_dict)




    def openCSVFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"CSV Files (*.csv)", options=options)
        self.pdc_paths.append(fileName)
        pdc_data = self.parser.readPDC(fileName)





    def openExcelFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose file", Path.home().as_posix(),"Excel Files (*.xlsx)", options=options)
        #sace data for gui to use later
        self.wire_report_paths.append(fileName)
        self.wire_report_list.addItem(fileName)
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