import sys
import time
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot, Qt
from UI_templates import main_window as main_window
# from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
from dwx_connector_MVC import DwxModel
from table_MVC import TableModel
import pandas as pd


class CallUi(QtWidgets.QMainWindow):
    """[summary]

    Args:
        QtWidgets ([type]): [description]
    """    

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.dwx_MVC = DwxModel()

        self.ui = main_window.Ui_MainWindow()

        self.ui.setupUi(self)

        self.setUpBtnconnect()

        self.prep_new_trade = None


        #ADD textlabel function to be loaded, similar to setupBtnconnect
        # also for text edits,
        #writing functions instead of loading in the __init__ will make the code more organized.

        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]

        data = pd.DataFrame(data)

        self.table_model = TableModel(data)
        self.ui.tableView.setModel(self.table_model)

        #Disable Execute Trade button if the currency pair is changed.
        self.ui.CURRENCY_PAIRS_COMBOBOX.currentTextChanged.connect(self.disable_execute_trade_btn)
        
    def disable_execute_trade_btn(self):
        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(False)


    def setUpBtnconnect(self):   
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(DwxModel)
        test_hist_req_data = [
            {'_symbol': 'EURUSD', '_timeframe': 1440, '_start': '2021.01.01 00:00:00', '_end': pd.Timestamp.now().strftime('%Y.%m.%d %H.%M.00') }
        ]
        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(self.dwx_MVC.send_hist_request)
        self.ui.PREPARE_NEW_TRADE_BTN.clicked.connect(self.prepare_new_trade)
        self.ui.EXECUTE_NEW_TRADE_BTN.clicked.connect(self.execute_new_trade)
        # self.ui.tableView.setRowCount(5)
        # self.ui.pushButton.clicked.connect(self.myFunction)

    # def myFunction(self):
    #     os.system("ipconfig")
    #     # raw_input()


    def prepare_new_trade(self):
        
        _symbol = self.ui.CURRENCY_PAIRS_COMBOBOX.currentText()
        if _symbol not in [self.ui.CURRENCY_PAIRS_COMBOBOX.itemText(i) for i in range(self.ui.CURRENCY_PAIRS_COMBOBOX.count())]:
            _symbol = 'EURUSD'
        #Check if the text entered is a valid currency pair that can be operated on ie. existing pairs on the list.
        #Else default value is EURUSD
        
        _order = 'SELL' if self.ui.BUY_SELL_SLIDER.sliderPosition() else 'BUY'
        #Default value of sider is 'SELL' (1)

        _timeframe = 15

        new_trade_dict = {
            '_symbol': _symbol,
            '_order': _order,
            '_timeframe': _timeframe
        }
        self.prep_new_trade = self.dwx_MVC.prepare_new_trade(new_trade_dict)
        print('Completed')
        self.ui.PIP_VALUE_TEXT.setText(str(round(self.prep_new_trade.pip_value, 4)))
        self.ui.ATR_IN_PIPS_TEXT.setText(str(round(self.prep_new_trade.atr_in_pips, 2)))
        self.ui.LOT_SIZE_TEXT.setText(str(str(round(self.prep_new_trade.lot_size, 2))))
        self.ui.RISK_AMOUNT_TEXT.setText(str(round(self.prep_new_trade.risk_amount, 4)))
        self.ui.ACCOUNT_BALANCE_TEXT.setText(str(self.prep_new_trade.account_info['account_equity']))
        self.ui.STOP_LOSS_TEXT.setText(str(round(self.prep_new_trade.stop_loss, 5)))
        self.ui.TAKE_PROFIT_TEXT.setText(str(round(self.prep_new_trade.take_profit, 5)))
        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(True)


    def execute_new_trade(self):
        try:
            self.dwx_MVC.new_trade(
                {
                '_action': 'OPEN',
                '_type': self.ui.BUY_SELL_SLIDER.sliderPosition(),      #1 for SELL, O for BUY 
                '_symbol': self.prep_new_trade._symbol,
                '_price': 0.0,                                          #Refers to current price value
                '_SL': self.prep_new_trade.atr_in_pips * self.prep_new_trade.sl_multiplier * 10, # SL/TP in POINTS, not pips.
                '_TP': self.prep_new_trade.atr_in_pips * self.prep_new_trade.tp_multiplier * 10,
                '_comment': self.prep_new_trade.account_info,
                '_lots': round(self.prep_new_trade.lot_size, 2),
                '_magic': 123456,
                '_ticket': 0              
                },
                {
                    '_order': 'full'
                }
            )
        except Exception as e:
            _exstr = "Exception Type {0}. Args:\n{1!r}"
            _msg = _exstr.format(type(e).__name__, e.args)
            print(_msg)

        

def setUpWindow():
    """
    Initialize app window
    """    
    app = QtWidgets.QApplication(sys.argv)
    nowWindow = CallUi()
    nowWindow.show()
    sys.exit(app.exec_())
