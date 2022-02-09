import sys, openpyxl, os, inputparser, igraph
from pathlib import Path
from inputparser import InputParser
from graphmanager import *
from PySide2 import QtWidgets, QtUiTools
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QRect, QFile, QIODevice, QObject
from openpyxl import Workbook, load_workbook

class App(QMainWindow):
    # setup UI and create parser
    def __init__(self):
        super().__init__()
        self.parser = InputParser()
        self.graph = GraphManager()
        self.wire_graph = self.graph.g
        self.setup_ui()

    def setup_ui(self):
        #stacked widget is the container that can be swapped out to change pages
        self.stacked_widget = QStackedWidget()

        self.stacked_widget.setMinimumSize(500, 400)
        self.stacked_widget.setWindowTitle("Paccar Wire Validation Tool")


        front_page = QWidget()
        #dictionary that contains all pages for navigation
        self.pages = {"front": front_page}

        #front page settup. nothing much here
        front_page_layout = QGridLayout()
        self.stacked_widget.addWidget(front_page)
        front_page.setLayout(front_page_layout)
        font = QFont("Helvetica", 20)
        welcome = QLabel("Paccar Wire Validation Tool")
        welcome.setFont(font)
        welcome.setAlignment(Qt.AlignCenter)
        front_page_layout.addWidget(welcome, 0, 0)

        #add button to go to nexxt page
        file_page_1_button = QPushButton("Next")
        file_page_1_button.clicked.connect(lambda : self.goto_page("file_picker"))
        front_page_layout.addWidget(file_page_1_button, 1, 0)

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
            next_wire_report_button.clicked.connect(lambda : self.openExcelFileDialog(next_wire_report_button))
            path_label = QLabel("File Path")
            left_widget_layout.insertRow(left_widget_layout.rowCount() - 1, next_wire_report_button)



        def add_PDC():
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
        add_wire_button.clicked.connect(add_wire_report)
        left_widget_layout.addRow(add_wire_button)

        #right side of page
        PDC_button = QPushButton("Choose PDC...")
        right_widget_layout.addRow(PDC_button)
        add_PDC_button = QPushButton("add PDC")
        add_PDC_button.clicked.connect(add_PDC)
        right_widget_layout.addRow(add_PDC_button)
        PDC_button.clicked.connect(lambda : self.openCSVFileDialog(PDC_button))

        #register current page
        self.stacked_widget.addWidget(file_picker_widgets)
        self.pages.update({"file_picker": file_picker_widgets})

        #button to next page
        #the next button is also the trigger to set up the next page since it relies on data collected from this current page
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.setup_wire_reports)
        next_button.clicked.connect(lambda: self.goto_page("wire_reports"))
        file_picker_layout.addWidget(next_button, 1, 0)

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

        #send files to input parser
        for path in self.pdc_paths:
            self.parser.readPDC(path)


        #create a new dictionary from combobox_dict where it is populated by strings instead of combobox objects
        def make_dict():
            for key, value in combo_box_dict.items():
                list = []
                for box in value:
                    list.append(box.currentText())
                self.wire_report_dict.update({key : list})
        #send reports to input Parser
        def send_reports():
            for path, fields in self.wire_report_dict.items():
                from_tuple = (fields[0], fields[1])
                to_tuple = (fields[2], fields[3])
                self.parser.readReport(path, from_tuple, to_tuple, fields[4], fields[5])
                for pdc in self.parser.pdcs.values():
                    self.graph.add_pdc(pdc)
                for report in self.parser.reports:
                    self.graph.add_report(report)
                print(self.graph.g)


        self.wire_report_list.itemClicked.connect(lambda: change_wire_report(self.wire_report_list.currentIndex()))
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
        #submit.clicked.connect(print_dict)
        submit.clicked.connect(make_dict)
        submit.clicked.connect(send_reports)

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
        #sace data for gui to use later
        self.wire_report_paths.append(fileName)
        self.wire_report_list.addItem(fileName)
        if fileName:
            button.setText(fileName)

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
