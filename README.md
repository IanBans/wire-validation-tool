# Overall Description
## Authors
Martin Armanasu, Jaden Breeland, Ian Bansenauer, and Ian McCleary.

## Product Perspective
The application is intended to make PACCAR employees' validation strategy less time consuming. By creating a streamlined output for each wire as well as computing automated validation checks, it can deliver more helpful information to employees when troubleshooting schematics. This will decrease the time it takes employees to find the source of error and increase productivity as a whole. Less time troubleshooting means more time spent elsewhere.

## Product Features
The application will be able to read in .xlsx and .csv spreadsheets representing wiring diagrams, and parse this information. A graphical interface will be implemented to allow users to select input files and designate which columns contain the needed information. The application will be able to export a human-readable summary of relevant information as an .xlsx spreadsheet.

## Operating Environment
The operating environment for the application shall be a desktop application for the Windows 10 operating system in an office environment. The program shall be written in Python using the Qt framework for developing graphical user interfaces. The program shall be simple enough to use for even non tech savvy users with minimal instruction.

## Functional Requirements and Features
<ul>
    <li>Read from and write to CSV and XLSX Filetypes</li>
    <li>Splice Handling</li>
    <li>Output Design and Format</li>
    <li>Build to Windows</li>
    <li>Graphical User Interface</li>
    <li>Minimum Wire CSA Check</li>
</ul>

<h2>Scope of Initial Release</h2>
The initial release of this program will read in a bill of materials for a set of wiring harnesses and trace the wires present in the Power Distribution Controller.
The list of wires will be output in a table containing the starting and ending components of the trace, a list of the traversed wires, and the splices encountered in the trace

## Scope of Subsequent Releases
Subsequent additions to this program may allow wire lengths to be read in by image recognition software.
The summary will also denote any wires which present a risk of overheating due to a mismatch between wire gauge and fuse rating.

## Limitations and Exclusions
This program will not be able to design, edit, or visually display wiring harness schematics.

## Build Instructions
To build the python script to a windows installer or windows exe with cx_freeze, install dependencies `pip3 install -r requirements.txt` then run `python3 build.py bdist_msi` or `python3 build.py setup_exe.`
 find the installer in the `build` folder
