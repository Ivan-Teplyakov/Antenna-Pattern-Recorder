import cx_Freeze
import sys
import matplotlib
import serial

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("AntennaPatternRecorder.py", base=base, icon="gui.ico")]

cx_Freeze.setup(
    name = "Antenna-Pattern-Recorder",
    options = {"build_exe": {"packages":["tkinter","matplotlib","serial"], "include_files":["gui.ico"]}},
    version = "0.01",
    description = "Graphic user application for Antenna Pattern Recorder",
    executables = executables
    )
