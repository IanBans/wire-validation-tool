"""
    Setup and config script for cx_Freeze.
    run 'python3 build.py bdist_msi' to build an
    MSI installer for the app
"""
import sys
from cx_Freeze import setup, Executable
# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

# set shortcut information
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",                      # Shortcut
     "StartMenuFolder",                      # Directory_
     "Wire Validation Tool",                 # Name
     "TARGETDIR",                            # Component_
     "[TARGETDIR]Wire Validation Tool.exe",  # Target
     None,                                   # Arguments
     None,                                   # Description
     None,                                   # Hotkey
     None,                                   # Icon
     None,                                   # IconIndex
     None,                                   # ShowCmd
     'TARGETDIR'                             # WkDir
     )
]

# creates the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('main.py', base=base, target_name='Wire Validation Tool')
]

setup(name='Wire Validation Tool',
      version='1.0',
      description='A tool to simplify BOM verification',
      options={'build_exe': build_options,
               'bdist_msi': bdist_msi_options},
      executables=executables)
