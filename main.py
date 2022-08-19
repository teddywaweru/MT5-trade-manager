"""
start
"""
import time
import ui_manipulation
import UI_templates.ui_converter as ui_conv
print(f'{time.asctime(time.localtime())}: Start of Application')


def setup():
    """
    Function code to initialize the setup window
    """
    ui_manipulation.setup_window()
    # print(time.asctime(time.localtime()))

if __name__ == "__main__":
    # convert .ui to .py. Only relevant for development stages.
    # print(time.asctime(time.localtime()))
    ui_conv.ui_converter()
    # #setup start
    setup()


    #color palette: https://coolors.co/ffffff-5a75a6-bbbdbe-e60540-0c0f0a
    #0c0f0a #ffffff #5a75a6 #bbbdbe #e60540 #0C1B33
    