import sys
from pathlib import Path
from PySide2.QtWidgets import QWidget, QStackedWidget, QMainWindow, QGridLayout, QLabel
from PySide2.QtWidgets import QFormLayout, QFileDialog, QComboBox, QPushButton, QListWidget
from PySide2.QtWidgets import QApplication, QCheckBox, QLineEdit, QFrame
from PySide2.QtGui import Qt, QPalette, QColor, QBrush
from openpyxl import load_workbook
from inputparser import InputParser
from export import ExportManager
from graphmanager import GraphManager
from csvconfig import CsvConfig


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
        self.parser = InputParser(self)
        self.graph = GraphManager(self)
        self.export = ExportManager(self)
        self.stacked_widget = QStackedWidget()
        self.wire_report_paths = []
        self.pdc_paths = []
        self.wire_report_configs = CsvConfig("configs.csv")
        self.wire_report_list = QListWidget()
        self.left_widget_layout = QFormLayout()
        self.right_widget_layout = QFormLayout()
        self.setupUI()

    def setupUI(self):
        """
            sets up UI elements and ties them together
        """
        # the stacked widget is the app container that swaps which widget is shown
        # Each widget is a page
        self.stacked_widget.setMinimumSize(500, 300)
        self.stacked_widget.resize(700, 400)
        self.stacked_widget.setWindowTitle('Paccar Wire Validation Tool')
        # self.pages collects all created pages for navigation
        self.pages = {}

        self.setupFilePage()
        self.stacked_widget.show()

        # Qwidget that contains paths of all wire Reports

    def goToPage(self, target):
        """
            target: string representation of the new page the user wants to display
            Changes the visible widget (the current viewable page) shown in the stacked widget
        """
        if target in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[target])

    # setup for picking all wire reports and PDC
    def setupFilePage(self):
        """
            sets up the file picker page
        """

        def createReportLabel(path, side):
            """
                path: the file the label represents
                side: determine if the label is created for a wire report or pdc
                adds wire report or pdc path label to the view that shows the path
            """

            def removeReport(label):
                """
                    removes the the specified label from the view and deletes the path
                    anywhere it was saved
                """

                if side == "wire":
                    for item in range(self.wire_report_list.count()):
                        if not self.wire_report_list.item(item):
                            continue
                        if self.wire_report_list.item(item).text() == cleanPathName(label.text()):
                            self.wire_report_list.takeItem(item)
                    self.wire_report_paths.remove(label.text())
                    self.left_widget_layout.removeRow(label)
                else:
                    self.pdc_paths.remove(label.text())
                    self.right_widget_layout.removeRow(label)
                if self.wire_report_paths and self.pdc_paths:
                    next_button.setEnabled(True)
                else:
                    next_button.setEnabled(False)

            remove_button = QPushButton("Remove")
            remove_button.setMaximumWidth(100)
            label = QLabel(path)
            remove_button.clicked.connect(lambda: removeReport(label))

            if side == "wire":
                self.left_widget_layout.addRow(label, remove_button)
            else:
                self.right_widget_layout.addRow(label, remove_button)

        def openCSVFileDialog():
            """
                opens the file picker to select a dirctory to save the output to
            """
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            filename, _ = QFileDialog.getOpenFileNames(self,
                                                       'Choose file',
                                                       Path.home().as_posix(),
                                                       'CSV Files (*.csv)',
                                                       options=options)
            for file in filename:
                if file not in self.pdc_paths:
                    self.pdc_paths.append(file)
                    createReportLabel(file, "pdc")
            if self.wire_report_paths and self.pdc_paths:
                next_button.setEnabled(True)
            else:
                next_button.setEnabled(False)

        def openExcelFileDialog():
            """
                opens the file picker sorted to .excel files
            """
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getOpenFileNames(self,
                                                       'Choose file',
                                                       Path.home().as_posix(),
                                                       'Excel Files (*.xlsx)',
                                                       options=options)

            for file in filename:
                if file not in self.wire_report_paths:
                    createReportLabel(file, "wire")
                    self.wire_report_paths.append(file)
                    self.wire_report_list.addItem(cleanPathName(file))
            if self.wire_report_paths and self.pdc_paths:
                next_button.setEnabled(True)
            else:
                next_button.setEnabled(False)

        def openSaveFileDialog():
            """
                opens file picker for saving files
            """
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            directory = QFileDialog.getExistingDirectory(self,
                                                        "choose file to save",
                                                        Path.home().as_posix())
            if directory:
                self.export.setDirectory(directory)
                save.setText(self.export.getSavePath())


        file_picker_widgets = QWidget()
        file_picker_layout = QGridLayout()
        file_picker_layout.setColumnStretch(0, 1)
        file_picker_layout.setRowStretch(0, 1)
        file_picker_layout.setColumnStretch(1, 1)
        next_button = QPushButton('Next')
        pdc_button = QPushButton('Add PDC')
        wire_button = QPushButton('Add Wire Reports')
        save = QPushButton("Choose Where to Save ...")
        save.clicked.connect(openSaveFileDialog)
        self.stacked_widget.addWidget(file_picker_widgets)
        file_picker_widgets.setLayout(file_picker_layout)

        self.left_widget_layout.setFormAlignment(Qt.AlignHCenter)
        self.right_widget_layout.setFormAlignment(Qt.AlignHCenter)
        file_picker_layout.addLayout(self.left_widget_layout, 0, 0)
        file_picker_layout.addLayout(self.right_widget_layout, 0, 1)

        # add buttons for wire reports to left side
        self.left_widget_layout.addRow(wire_button)
        wire_button.clicked.connect(openExcelFileDialog)

        # add buttons for pdc to right side
        self.right_widget_layout.addRow(pdc_button)
        pdc_button.clicked.connect(openCSVFileDialog)

        # register current page in page dict
        self.stacked_widget.addWidget(file_picker_widgets)
        self.pages.update({'file_picker': file_picker_widgets})

        next_button.clicked.connect(self.setupWireReports)
        next_button.clicked.connect(lambda: self.goToPage('wire_reports'))
        next_button.setEnabled(False)
        file_picker_layout.addWidget(next_button, 2, 0, 2, 2)
        file_picker_layout.addWidget(save, 1, 0, 1, 2)
        save.setMaximumWidth(200)
        next_button.setMaximumWidth(200)
        home = QPushButton("Home")
        home.clicked.connect(lambda: self.goToPage("file_picker"))
        home.setMinimumWidth(150)
        home_color = QPalette(QApplication.palette())
        home_color.setBrush(QPalette.Button, QBrush(QColor(165, 214, 255)))
        home.setPalette(home_color)
        file_picker_layout.addWidget(home, 2, 1, Qt.AlignRight)

    def setupWireReports(self):
        """
            creates page to customize column fields for each report
        """
        def makeDict():
            """
                create a new dictionary from combobox_dict
                where it is populated by strings instead of
                combobox objects
                Also checks if data needs to be written to or from csvConfig
            """
            counter = -1
            for key, value in combo_box_dict.items():
                counter += 1

                # check user wants to load wire_report_configuration
                if load_wire_report_dict[counter].currentIndex() != 0:
                    config = self.wire_report_configs.search(
                        load_wire_report_dict[counter].currentText())
                    del config[0]
                    wire_report_dict.update({key: config})
                    print("printing config: ", config)
                    continue

                # read combox_dict
                report_list = []
                for box in value:
                    report_list.append(box.currentText())

                # check if user wants to save a new wire report config
                if checkbox_dict[counter][0].isChecked():
                    new_config = []
                    new_config.append(checkbox_dict[counter][1].text())
                    for item in report_list:
                        new_config.append(item)
                    print(new_config)
                    self.wire_report_configs.add(new_config)
                wire_report_dict.update({key: report_list})

        def sendReports():
            """
                send reports to input Parser
                & print current graph data
            """
            # send pdc to input parser
            for path in self.pdc_paths:
                if path:
                    self.parser.readPDC(path)

            for path, fields in wire_report_dict.items():
                from_tuple = (fields[0], fields[1])
                to_tuple = (fields[2], fields[3])
                self.parser.readReport(path, from_tuple, to_tuple, fields[4], fields[5])

            for _, pdc in self.parser.getPDCs().items():
                self.graph.addPDC(pdc)
            for report in self.parser.getReports():
                self.graph.addReport(report)

            self.export.exportToExcel(self.graph.traceWires())

        def checkConfigSelection(combo_box, checkbox, line):
            combo_box.update()
            makeDict()
            print(combo_box.currentText())
            print(checkbox.checkState())
            if combo_box.currentIndex() != 0:
                checkbox.setEnabled(False)
                line.setEnabled(False)
            elif checkbox.isChecked():
                combo_box.setEnabled(False)
                line.setEnabled(True)
            elif combo_box.currentIndex == 0 and not checkbox.isChecked():
                combo_box.setEnabled(True)
                checkbox.setEnabled(True)
                line.setEnabled(True)

        wire_report_dict = {}
        # this list contains all the column fields names
        # necessary for reading the input
        fields_list = ['From Component',
                       'From Pin',
                       'To Component',
                       'To Pin',
                       'Wire CSA',
                       'Wire Name']

        page = QWidget()
        page_layout = QGridLayout()
        fields_selector = QStackedWidget()
        submit = QPushButton('Submit')

        # the Dictionary that contains all the wire column fields.
        # The key is the wire path and the value is a list of QComboBoxes
        # that contain wire fields
        combo_box_dict = {}

        self.wire_report_list.itemClicked.connect(
            lambda: fields_selector.setCurrentIndex(self.wire_report_list.currentIndex().row()))
        page.setLayout(page_layout)
        self.stacked_widget.addWidget(page)
        self.pages.update({'wire_reports': page})
        page_layout.addWidget(self.wire_report_list, 0, 0)

        page_layout.addWidget(fields_selector, 0, 1, Qt.AlignVCenter)

        # save and load wire harness configurations

        wire_csv_stacked_widget = QStackedWidget()
        # the following two vars are used to keep track of the state of above stacked widget
        checkbox_dict = {}
        load_wire_report_dict = {}
        page_layout.addWidget(wire_csv_stacked_widget, 1, 0, 1, 2, Qt.AlignHCenter)
        # change view of page according to which wire report is selected
        self.wire_report_list.itemClicked.connect(
            lambda: wire_csv_stacked_widget.setCurrentIndex(
                self.wire_report_list.currentIndex().row()))

        # create new widget for each wire report that manages wire csv configs
        # Each widget is stacked on each other in wire_csv_stacked_widget
        for x in range(self.wire_report_list.count()):
            container = QWidget()
            wire_csv_stacked_widget.addWidget(container)
            format_selector = QGridLayout()
            container.setLayout(format_selector)
            format_selector.addWidget(
                QLabel("Or select saved wire report format"), 0, 2)
            combo_box = QComboBox()
            combo_box.addItem("Choose Option")
            for row in self.wire_report_configs.returnAllNames():
                combo_box.addItem(row)
            load_wire_report_dict.update({x: combo_box})

            checkbox = QCheckBox()
            checkbox.setText("click here to save the above configuration for future use")
            checkbox.adjustSize()

            line = QLineEdit()
            line.setPlaceholderText("Enter the name of this configuration")
            line.setMaximumWidth(400)
            line.adjustSize()

            checkbox.stateChanged.connect(
                lambda: checkConfigSelection(combo_box, checkbox, line))
            combo_box.currentTextChanged.connect(
                lambda: checkConfigSelection(combo_box, checkbox, line))

            checkbox_dict.update({x: (checkbox, line)})
            format_selector.addWidget(combo_box, 1, 2)
            format_selector.addWidget(checkbox, 0, 0)
            format_selector.addWidget(line, 1, 0)
            format_selector.setSpacing(20)
            format_selector.setMargin(20)
            draw_line = QFrame()
            draw_line.setFrameShape(QFrame.VLine)
            draw_line.setFrameShadow(QFrame.Raised)
            format_selector.addWidget(draw_line, 0, 1, 3, 1)
            container.adjustSize()

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

        back = QPushButton("Back")
        back.clicked.connect(lambda: self.goToPage("file_picker"))
        home = QPushButton("Home")
        home.clicked.connect(lambda: self.goToPage("file_picker"))
        home.setMinimumWidth(150)
        home_color = QPalette(QApplication.palette())
        home_color.setBrush(QPalette.Button, QBrush(QColor(165, 214, 255)))
        home.setPalette(home_color)
        page_layout.addWidget(home, 3, 1, Qt.AlignRight)
        page_layout.addWidget(back, 2, 0, 1, 1)
        page_layout.addWidget(submit, 3, 0, 1, 1)

        submit.clicked.connect(makeDict)
        submit.clicked.connect(sendReports)

def reportError(error_code):
    """
    error_code: specifies what type of error recieved
    used by other modules to report errors encountered
    """
    print(error_code)


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


def cleanPathName(path):
    """
        path: a string conatining the full path to a file
        Returns a new string by striping a path name so that only the file name remains
    """
    i = -1
    while path[i] != '/' and path[i] != '\\':
        i = i - 1
    return path[i + 1:]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = App()
    sys.exit(app.exec_())
