"""[summary]
"""
import sys
import time
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot, Qt
from UI_templates import main_window as main_window
# from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
from dwx_connector_mvc import DwxModel
from table_MVC import TableModel
import pandas as pd


class CallUi(QtWidgets.QMainWindow):
    """[summary]

    Args:
        QtWidgets ([type]): [description]
    """
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.dwx_mvc = DwxModel()

        self.ui = main_window.Ui_MainWindow()

        self.ui.setupUi(self)

        self.setup_btn_connect()

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
        """[summary]
        """
        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(False)

    def order_type_btn_clicked(self, order_btn):
        """Styling & disabling for order buttons depending on which one is selected.

        Args:
            order_btn (QButton Object): The button that has been checked.
            Options are: SELL, BUY, SELL LIMIT, BUY LIMIT, SELL STOP, BUY STOP
        """               
        for i in [
            self.ui.SELL_BTN, self.ui.SELL_LMT_BTN,
            self.ui.BUY_BTN, self.ui.BUY_LMT_BTN
        ]:
            if i != order_btn:
                if i.isChecked():
                    i.setChecked(False)
                    i.setStyleSheet('')

        if order_btn.isChecked():
            if order_btn.text() == 'SELL':
                self.ui.SELL_BTN.setStyleSheet(
            'background-color: #A01;'
            'border-style: outset;'
            'border-width: 2px;'
            # 'border-color: beige;'
                )

            elif order_btn.text() == 'BUY':
                self.ui.BUY_BTN.setStyleSheet(
            'background-color: #ABF;'
            'border-style: outset;'
            'border-width: 2px;'
            # 'border-color: beige;'
                )

        else: order_btn.setStyleSheet('')

    def order_strategy_btn_clicked(self, order_strategy):
        """Styling & disabling for strategy buttons depending on
         which ones is selected

        Args:
            order_strategy (QButton Object): The button that has been checked.
            Options are: single Order Trade, or Split Order Trade
        """        
        for i in [
            self.ui.SPLIT_TRADE_BTN, self.ui.SINGLE_TRADE_BTN
        ]:
            if i != order_strategy:
                i.setChecked(False)
                i.setStyleSheet('')

        if order_strategy.isChecked():
            order_strategy.setStyleSheet('background-color: #AED;'
                            'border-style: outset;'
                            'border-width: 2px;'
                            'border-color: beige;'
                            )
        else: order_strategy.setStyleSheet('')
    
            


    def setup_btn_connect(self):
        """[Initiate button functions]
        """
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(DwxModel)
        test_hist_req_data = [
            {'_symbol': 'EURUSD',
            '_timeframe': 1440,
            '_start': '2021.01.01 00:00:00',
            '_end': pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00') }
        ]
        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(self.dwx_mvc.send_hist_request)
        self.ui.PREPARE_NEW_TRADE_BTN.clicked.connect(self.prepare_new_trade)
        self.ui.EXECUTE_NEW_TRADE_BTN.clicked.connect(self.execute_new_trade)

        self.ui.SELL_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_BTN))

        self.ui.BUY_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_BTN))

        self.ui.BUY_LMT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_LMT_BTN))

        self.ui.SELL_LMT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_LMT_BTN))

        self.ui.SPLIT_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.SPLIT_TRADE_BTN))
        
        self.ui.SINGLE_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.SINGLE_TRADE_BTN))
        # self.ui.tableView.setRowCount(5)
        # self.ui.pushButton.clicked.connect(self.myFunction)


    def prepare_new_trade(self):
        """[summary]
        """

        #Check if the text entered is a valid currency pair that
        # can be operated on ie. existing pairs on the list.
        #Else default value is EURUSD
        _symbol = self.ui.CURRENCY_PAIRS_COMBOBOX.currentText()
        if _symbol not in [self.ui.CURRENCY_PAIRS_COMBOBOX.itemText(i) for i in range(self.ui.CURRENCY_PAIRS_COMBOBOX.count())]:
            print('Select a Currency Pair')
            return

        _order = ''
        #Iterate through the order types to find the selected one
        #Do nothing if none is selected
        for i in [
            self.ui.SELL_BTN,
            self.ui.SELL_LMT_BTN,
            self.ui.BUY_BTN,
            self.ui.BUY_LMT_BTN
                ]:
            if i.isChecked():
                _order = i.text()
        
        if _order == '':
            print('Select an order type.')
            return


        _timeframe = 15

        new_trade_dict = {
            '_symbol': _symbol,
            '_order': _order,
            '_timeframe': _timeframe
        }
        try:
            self.prep_new_trade = self.dwx_mvc.prepare_new_trade(new_trade_dict)

            self.ui.PIP_VALUE_TEXT.setText(str(round(self.prep_new_trade.pip_value, 4)))
            self.ui.ATR_IN_PIPS_TEXT.setText(str(round(self.prep_new_trade.atr_in_pips, 2)))
            self.ui.LOT_SIZE_TEXT.setText(str(str(round(self.prep_new_trade.lot_size, 2))))
            self.ui.RISK_AMOUNT_TEXT.setText(str(round(self.prep_new_trade.risk_amount, 4)))
            self.ui.ACCOUNT_BALANCE_TEXT.setText(str(self.prep_new_trade.account_info['account_equity']))
            self.ui.STOP_LOSS_TEXT.setText(str(round(self.prep_new_trade.stop_loss, 5)))
            self.ui.TAKE_PROFIT_TEXT.setText(str(round(self.prep_new_trade.take_profit, 5)))
            self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(True)

        except Exception as ex:
            _exstr = "Exception Type {0}. Args:\n{1!r}"
            _msg = _exstr.format(type(ex).__name__, ex.args)
            print(_msg)

    def execute_new_trade(self):
        """[summary]
        """
        trade_strategy = ''
        #iterate to select the trade strategy that is selected.
        #split the trade, or make a single order
        for i in [
            self.ui.SINGLE_TRADE_BTN,
            self.ui.SPLIT_TRADE_BTN
        ]:
            if i.isChecked():      
                trade_strategy = i.text()

        if trade_strategy == '':
            print('Select a trading strategy.')
            return

        order_type = {
            'SELL': 1, 'BUY': 0, 'SELL LIMIT': 2
        }

        try:
            self.dwx_mvc.new_trade(
                {
                '_action': 'OPEN',
                '_type': order_type[self.prep_new_trade._order],      #1 for SELL, O for BUY
                '_symbol': self.prep_new_trade._symbol,
                '_price': 0.0,                  #Refers to current price value
                # SL/TP in POINTS, not pips.
                '_SL': self.prep_new_trade.atr_in_pips * self.prep_new_trade.sl_multiplier * 10, 
                '_TP': self.prep_new_trade.atr_in_pips * self.prep_new_trade.tp_multiplier * 10,
                '_comment': self.prep_new_trade.account_info,
                '_lots': round(self.prep_new_trade.lot_size, 2),
                '_magic': 123456,
                '_ticket': 0
                },
                {
                    'trade_strategy': trade_strategy,
                    'split_ratio': 0.5
                }
            )
        except Exception as ex:
            _exstr = "Exception Type {0}. Args:\n{1!r}"
            _msg = _exstr.format(type(ex).__name__, ex.args)
            print(_msg)


def setup_window():
    """
    Initialize app window
    """
    app = QtWidgets.QApplication(sys.argv)
    now_window = CallUi()
    now_window.show()
    sys.exit(app.exec_())
