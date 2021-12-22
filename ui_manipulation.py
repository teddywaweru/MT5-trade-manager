import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot, Qt
from pathlib import Path
import UI_templates.main_window as main_window
from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx


class CallUi(QtWidgets.QMainWindow):
    """[summary]

    Args:
        QtWidgets ([type]): [description]
    """    

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setUpBtnconnect()


        # self.table = QtWidgets.QTableView()

        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]

        self.model = TableModel(data)
        self.ui.tableView.setModel(self.model)



    def setUpBtnconnect(self):   
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(initialize_dwx_connector)
        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(send_hist_request)
        # self.ui.tableView.setRowCount(5)
        # self.ui.pushButton.clicked.connect(self.myFunction)

    # def myFunction(self):
    #     os.system("ipconfig")
    #     # raw_input()

class TableModel(QtCore.QAbstractTableModel):
    """Creating a Table Model for PyQt5 using the procedure:
    https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/

    Args:
        QtCore ([type]): [description]
    """    
    def __init__(self,data):
        super(TableModel,self).__init__()
        self._data = data

    def data(self,index,role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    
def setUpWindow():
    """
    Initialize app window
    """    
    app = QtWidgets.QApplication(sys.argv)
    nowWindow = CallUi()
    nowWindow.show()
    sys.exit(app.exec_())

@Slot()
def say_hello():
    print('Button Press recognized.')

@Slot()
def initialize_dwx_connector():
    #create connector object
    global ZMQ_
    ZMQ_ =  dwx()
    print('Zero MQ initialized')

    #subscribe to EURUSD
    ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_()
    print('Subscribed to EURUSD')

@Slot()
def send_hist_request():
    ZMQ_._DWX_MTX_SEND_HIST_REQUEST_()