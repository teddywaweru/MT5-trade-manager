"""[summary]
"""
import sys
import time
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
# from PySide6 import QtCore, QtGui, QtWidgets
# from PySide6.QtCore import Slot, Qt
from UI_templates import main_window
# from dwx_MVC import DwxModel
from dwx_connector import connect_dwx as conn_dwx
from table_MVC import TableModel
import pandas as pd


class CallUi(QtWidgets.QMainWindow):
    """[summary]

    Args:
        QtWidgets ([type]): [description]
    """
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # Load DWX Connection Object
        # self.dwx_mvc = DwxModel()
        self.dwx, self.dwx_mvc = conn_dwx()
        

        # Create Main UI Instance
        self.ui = main_window.Ui_MainWindow()


        #Load Main UI objects
        self.ui.setupUi(self)

        # Load widget functions (BTN, COMBOBOX) for reacting to actions
        self.setup_btn_connect()

        self.setup_combobox_connect()

        #New Prepared Trade Object
        self.prep_new_trade = None

        #List of Order Buttons. For iterations.
        self.order_btns = [
            self.ui.SELL_BTN, self.ui.SELL_LIMIT_BTN,
            self.ui.BUY_BTN, self.ui.BUY_LIMIT_BTN
        ]

        #List of Order Strategy buttons. For iterations
        self.order_strategy_btns = [
            self.ui.SINGLE_TRADE_BTN,
            self.ui.MINIMAL_TRADE_BTN,
            self.ui.TWO_WAY_SPLIT_TRADE_BTN,
            self.ui.THREE_WAY_SPLIT_TRADE_BTN
        ]

        #List of Timeframe buttons. For iterations
        self.order_timeframe_btns = [
            self.ui.MIN_1440_BTN, self.ui.MIN_15_BTN, self.ui.MIN_60_BTN
            ]

        #ist of instrument comboboxes. For iterations
        self.instr_comboboxes = [
            self.ui.CURRENCY_PAIRS_METALS_COMBOBOX, self.ui.COMMS_INDCS_COMBOBOX
            ]




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


    def disable_execute_trade_btn(self):
        """Function to disable the Execute Trade button.
        """
        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(False)

    #Change the current text in the alternate combobox to None
    def combobox_text_changed(self, instr_combobox):
        """_summary_

        Args:
            instr_combobox (combobox Object): Combobox object that created the signal
        """  
        #Disable the Execute button.      
        self.disable_execute_trade_btn()

        #If current text is None, return
        if instr_combobox.currentText() == '':
            return

        #Else iterate through the list of comboboxes
        for i in self.instr_comboboxes:
            #If i is not the currently altered combobox, alter the text to blank
            if i != instr_combobox:
                i.setCurrentText('')
        print('Current Instrument to trade: {}.'.format(instr_combobox.currentText()))

    def order_type_btn_clicked(self, order_btn):
        """Styling & disabling for order buttons depending on which one is selected.

        Args:
            order_btn (QButton Object): The button that has been checked.
            Options are: SELL, BUY, SELL LIMIT, BUY LIMIT, SELL STOP, BUY STOP
        """
        for i in self.order_btns:
            if i != order_btn:
                if i.isChecked():
                    i.setChecked(False)
                    i.setStyleSheet('')

        if order_btn.isChecked():
            if order_btn.text() in ['SELL', 'SELL LIMIT']:
                order_btn.setStyleSheet(
            'background-color: #A01;'
            'border-style: outset;'
            'border-width: 2px;'
            # 'border-color: beige;'
                )

            elif order_btn.text() in ['BUY', 'BUY LIMIT']:
                order_btn.setStyleSheet(
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
        for i in self.order_strategy_btns:
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

    def order_timeframe_btn_clicked(self, order_timeframe):
        """[summary]

        Args:
            order_timeframe ([type]): [description]
        """

        #Disable the Execute button.      
        self.disable_execute_trade_btn()


        for i in self.order_timeframe_btns:
            if i != order_timeframe:
                if i.isChecked():
                    i.setChecked(False)
                    i.setStyleSheet('')

            if order_timeframe.isChecked():
                order_timeframe.setStyleSheet('background-color: #A3D;'
                            'border-style: outset;'
                            'border-width: 2px;'
                            'border-color: beige;'
                            )
            else: order_timeframe.setStyleSheet('')


    def setup_btn_connect(self):
        """[Initiate button functions]
        """
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(self.dwx_mvc.get_trades)
        # test_hist_req_data = [
        #     {'_symbol': 'EURUSD',
        #     '_timeframe': 1440,
        #     '_start': '2021.01.01 00:00:00',
        #     '_end': pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00') }
        # ]
        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(self.dwx_mvc.send_hist_request)
        self.ui.PREPARE_NEW_TRADE_BTN.clicked.connect(self.prepare_new_trade)
        self.ui.EXECUTE_NEW_TRADE_BTN.clicked.connect(self.execute_new_trade)

        self.ui.SELL_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_BTN))

        self.ui.BUY_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_BTN))

        self.ui.BUY_LIMIT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_LIMIT_BTN))

        self.ui.SELL_LIMIT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_LIMIT_BTN))

        self.ui.TWO_WAY_SPLIT_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.TWO_WAY_SPLIT_TRADE_BTN))
        
        self.ui.THREE_WAY_SPLIT_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.THREE_WAY_SPLIT_TRADE_BTN))
        
        self.ui.SINGLE_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.SINGLE_TRADE_BTN))

        self.ui.MINIMAL_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.MINIMAL_TRADE_BTN)
        )

        self.ui.MIN_15_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_15_BTN)
        )

        self.ui.MIN_1440_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_1440_BTN)
        )

        self.ui.MIN_60_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_60_BTN)
        )


        # self.ui.tableView.setRowCount(5)
        # self.ui.pushButton.clicked.connect(self.myFunction)

    def setup_combobox_connect(self):
        """_summary_
        """   

        self.ui.COMMS_INDCS_COMBOBOX.currentTextChanged.connect(
            lambda: self.combobox_text_changed(self.ui.COMMS_INDCS_COMBOBOX)
        )
        self.ui.CURRENCY_PAIRS_METALS_COMBOBOX.currentTextChanged.connect(
            lambda: self.combobox_text_changed(self.ui.CURRENCY_PAIRS_METALS_COMBOBOX)
        )


    def prepare_new_trade(self):
        """[summary]
        """

        #Check if the text entered is a valid currency pair that
        # can be operated on ie. existing pairs on the list.
        for i in self.instr_comboboxes:
            if i.currentText() != '':
                _symbol = i.currentText()
                
                #Ensure that the text is in the current list of traded instruments.
                if _symbol not in [i.itemText(j) for j in range(i.count())]:
                    print('Select a Valid Instrument.')

                    return

        _order = ''
        #Iterate through the order types to find the selected one
        for i in self.order_btns:
            if i.isChecked():
                _order = i.text()
        
        if _order == '':
            print('Select an order type.')
            return

        #Iterate through the order timeframes to find the selected one
        #Do nothing if none is selected
        _timeframe = ''
        for i in self.order_timeframe_btns:
            if i.isChecked():
                _timeframe = int(''.join([n for n in i.objectName().split('_') if n.isdigit()]))
        
        if _timeframe == '':
            print('Select an order Timeframe.')
            return


        if self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText() != '':
            try:
                buy_sell_limit = float(self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText())
            except Exception:
                print('Buy/Sell Limit is not a valid Double value')
                return
        else: buy_sell_limit = ''


        new_trade_dict = {
            '_symbol': _symbol,
            '_order': _order,
            '_timeframe': _timeframe,
            'buy_sell_limit': buy_sell_limit
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
        for i in self.order_strategy_btns:
            if i.isChecked():
                trade_strategy = i.text()

        if trade_strategy == '':
            print('Select a trading strategy.')
            return

        order_type = {
            'SELL': 1, 'BUY': 0, 'SELL LIMIT': 2, 'BUY LIMIT': 3
        }

        try:
            self.dwx_mvc.new_trade(
                {
                '_action': 'OPEN',
                '_type': order_type[self.prep_new_trade.trade_dict['_order']],      #1 for SELL, O for BUY
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
                    'split_ratio': 0.5,
                    'split_ratio_2' : 0.5
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
    # print(time.time())
    print(time.time())
    now_window.show()
    sys.exit(app.exec_())
