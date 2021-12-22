"""
start
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os
import sys
import ui_manipulation
import UI_templates.ui_converter as ui_conv


def setup():
    """
    Function code to initialize the setup window
    """    
    ui_manipulation.setUpWindow()
    # raw_input()

if __name__ == "__main__":
    # convert .ui to .py. Only relevant for development stages.
    ui_conv.ui_converter()
    #setup start
    setup()
