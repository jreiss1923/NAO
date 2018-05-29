import sys
from cx_Freeze import setup, Executable

additional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(
    name = "Face Detection & Conversation",
    version = "2.7",
    description = "Detects saved users and starts an appropriate conversation with them",
    options = {'build_exe': {'includes': additional_mods}},
    executables = [Executable("FacialRecognitionDetection.py", base = "Win32GUI")])