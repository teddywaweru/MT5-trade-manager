"""
start
"""
# from PyQt5 import QtCore, QtGui, QtWidgets
# from pathlib import Path
# import os
# import sys
import time
import ui_manipulation
import UI_templates.ui_converter as ui_conv
print('{}: Start of Application'.format(time.time()))


def setup():
    """
    Function code to initialize the setup window
    """
    ui_manipulation.setup_window()
    # print(time.time())
    # raw_input()

if __name__ == "__main__":
    # convert .ui to .py. Only relevant for development stages.
    # print(time.time())
    ui_conv.ui_converter()
    #setup start
    setup()