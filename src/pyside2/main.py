import sys
from pathlib import Path
from PySide2.QtWidgets import QWidget, QStackedWidget, QMainWindow, QGridLayout, QLabel
from PySide2.QtWidgets import QFormLayout, QFileDialog, QComboBox, QPushButton, QListWidget
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QFont, Qt
from openpyxl import load_workbook
from inputparser import InputParser
from graphmanager import GraphManager


class App(QMainWindow):
    """
       App: the main UI and entry point for the application
       Fields:
        parser: input parser object to get input from files
        graph: GraphManager instance to store data into.
        stacked_widget: the main window container
       Methods:
        setupUI(): creates the UI structure and elements
        readColumnNames(): helper function to fill the column drop down lists
        goToPage(): sets stacked_widget page to target
        setupFilePage(): sets up file picker page
        setupWireReports(): sets up column picker for each report
        readColumnNames(): helper function for wire report dropdowns
    """
    # sets up UI and create parser and GraphManager instances
    def __init__(self):
        super().__init__()
        self.parser = InputParser()
        self.graph = GraphManager()
        self.stacked_widget = QStackedWidget()
        self.wire_report_paths = []
        self.wire_report_list = QListWidget()
        self.pdc_paths = []

        self.setupUI()

    def setupUI(self):
        """
            sets up UI elements and ties them together
        """

        front_page = QWidget()
        welcome = QLabel('Paccar Wire Validation Tool')
        font = QFont('Helvetica', 20)
        file_page_1_button = QPushButton('Next')

        self.stacked_widget.setMinimumSize(500, 400)
        self.stacked_widget.setWindowTitle('Paccar Wire Validation Tool')

        # dictionary that contains all pages for navigation
        self.pages = {'front': front_page}

        # sets up front page
        front_page_layout = QGridLayout()
        self.stacked_widget.addWidget(front_page)
        front_page.setLayout(front_page_layout)

        welcome.setFont(font)
        welcome.setAlignment(Qt.AlignCenter)
        front_page_layout.addWidget(welcome, 0, 0)

        # add button to go to next page
        file_page_1_button.clicked.connect(lambda: self.goToPage('file_picker'))
        front_page_layout.addWidget(file_page_1_button, 1, 0)

        self.setupFilePage()
        self.stacked_widget.show()

    # pages so far: front, file_picker, wire_reports
    def goToPage(self, target):
        """
            target: a string in the pages dictionary
            sets current widget to the target page
            in the page dictionary
        """
        if target in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[target])

    # setup for picking all wire reports and PDC
    def setupFilePage(self):
        """
            sets up the file picker page
        """

        def chooseWireReport():
            """
                adds wire report picker button to view
            """
            next_wire_report_button = QPushButton("Choose Wire Report")
            next_wire_report_button.clicked.connect(
                lambda: self.openExcelFileDialog(next_wire_report_button))
            left_widget_layout.insertRow(left_widget_layout.rowCount() - 1, next_wire_report_button)

        def choosePDC():
            """
                adds choose pdc button to view
            """
            next_pdc_button = QPushButton("Choose PDC")
            next_pdc_button.clicked.connect(lambda: self.openCSVFileDialog(next_pdc_button))

            right_widget_layout.insertRow(right_widget_layout.rowCount() - 1, next_pdc_button)

        file_picker_widgets = QWidget()
        file_picker_layout = QGridLayout()
        next_button = QPushButton('Next')
        pdc_button = QPushButton('Choose PDC...')
        add_pdc_button = QPushButton('add PDC')
        wire_button = QPushButton('Choose Wire Report...')
        add_wire_button = QPushButton('add wire report')

        self.stacked_widget.addWidget(file_picker_widgets)
        file_picker_widgets.setLayout(file_picker_layout)

        left_widget_layout = QFormLayout()
        right_widget_layout = QFormLayout()
        file_picker_layout.addLayout(left_widget_layout, 0, 0)
        file_picker_layout.addLayout(right_widget_layout, 0, 1)

        # add buttons for wire reports to left side
        left_widget_layout.addRow(wire_button)
        wire_button.clicked.connect(lambda: self.openExcelFileDialog(wire_button))
        add_wire_button.clicked.connect(chooseWireReport)
        left_widget_layout.addRow(add_wire_button)

        # add buttons for pdc to right side

        right_widget_layout.addRow(pdc_button)
        add_pdc_button.clicked.connect(choosePDC)
        right_widget_layout.addRow(add_pdc_button)
        pdc_button.clicked.connect(lambda: self.openCSVFileDialog(pdc_button))

        # register current page in page dict
        self.stacked_widget.addWidget(file_picker_widgets)
        self.pages.update({'file_picker': file_picker_widgets})

        # add button to next page
        # the next button is also the trigger
        # to set up the next page since it relies on data
        # collected from this current page

        next_button.clicked.connect(self.setupWireReports)
        next_button.clicked.connect(lambda: self.goToPage('wire_reports'))
        file_picker_layout.addWidget(next_button, 1, 0)

    def setupWireReports(self):
        """
            customize column fields for each report
        """
        wire_report_dict = {}
        # this list contains all the column fields names
        # necessary for reading the input
        fields_list = ['From Component',
                       'From Pin',
                       'To Component',
                       'To Pin',
                       'Wire CSA',
                       'Description']

        page = QWidget()
        page_layout = QGridLayout()
        fields_selector = QStackedWidget()
        submit = QPushButton('Submit')
        # the Dictionary that contains all the wire column fields.
        # The key is the wire path and the value is a list of QComboBoxes
        # that contain wire fields
        combo_box_dict = {}

        # send files to input parser
        for path in self.pdc_paths:
            self.parser.readPDC(path)

        def makeDict():
            """
                create a new dictionary from combobox_dict
                where it is populated by strings instead of
                combobox objects
            """
            for key, value in combo_box_dict.items():
                report_list = []
                for box in value:
                    report_list.append(box.currentText())
                wire_report_dict.update({key: report_list})

        def sendReports():
            """
                send reports to input Parser
                & print current graph data
            """
            for path, fields in wire_report_dict.items():
                from_tuple = (fields[0], fields[1])
                to_tuple = (fields[2], fields[3])
                self.parser.readReport(path, from_tuple, to_tuple, fields[4], fields[5])

            for _, pdc in self.parser.getPDCs().items():
                self.graph.addPDC(pdc)

            for report in self.parser.getReports():
                self.graph.addReport(report)

            self.graph.printNodes()
            self.graph.printEdges()

        self.wire_report_list.itemClicked.connect(
            lambda: fields_selector.setCurrentIndex(self.wire_report_list.currentIndex().row()))
        page.setLayout(page_layout)
        self.stacked_widget.addWidget(page)
        self.pages.update({'wire_reports': page})
        page_layout.addWidget(self.wire_report_list, 0, 0)

        page_layout.addWidget(fields_selector, 0, 1)

        # create combo boxes and add them to page
        for wire_report in self.wire_report_paths:

            fields_layout = QFormLayout()
            fields_container = QWidget()
            combo_box_list = []
            fields_container.setLayout(fields_layout)
            combo_box_dict.update({wire_report: combo_box_list})
            column_names = readColumnNames(wire_report)

            for i, _ in enumerate(fields_list):
                combo_box = QComboBox()
                label = QLabel(fields_list[i])
                combo_box.addItem('Choose Option')

                for name in column_names:
                    combo_box.addItem(name)

                combo_box_list.append(combo_box)
                combo_box.setCurrentIndex(0)
                fields_layout.addRow(combo_box, label)

            fields_selector.addWidget(fields_container)

        fields_selector.setCurrentIndex(0)

        page_layout.addWidget(submit, 2, 0)
        submit.clicked.connect(makeDict)
        submit.clicked.connect(sendReports)

    def openCSVFileDialog(self, button):
        """
            opens the file picker sorted to .csv files
            sets the button to the file name picked
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  'Choose file',
                                                  Path.home().as_posix(),
                                                  'CSV Files (*.csv)',
                                                  options=options)
        if filename:
            self.pdc_paths.append(filename)
            button.setText(filename)

    def openExcelFileDialog(self, button):
        """
            button: the button where to display filename
            opens the file picker sorted to .excel files
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  'Choose file',
                                                  Path.home().as_posix(),
                                                  'Excel Files (*.xlsx)',
                                                  options=options)

        if filename:
            button.setText(filename)
            self.wire_report_paths.append(filename)
            self.wire_report_list.addItem(filename)


def readColumnNames(filename):
    """
        filename: full file path of report file
        gets first line of worksheet
        and returns it as a list
        helper function for UI drop down boxes
    """
    names = []
    if filename:
        workb = load_workbook(filename, read_only=True)
        sheet = workb.active

        for first_row in sheet.iter_rows(1, 1, 1, sheet.max_column, True):
            names = list(first_row)
    return names


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())
