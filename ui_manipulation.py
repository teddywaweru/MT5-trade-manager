"""[summary]
"""

# pylint: disable=broad-except


import sys
import time
import asyncio
import traceback
from PyQt5 import QtWidgets
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter
# from pathlib import Path
# from PySide6 import QtCore, QtGui, QtWidgets
# from PySide6.QtCore import Slot, Qt
from UI_templates import main_window
# from dwx_MVC import DwxModel
from mt_connector import connect_mt as conn_mt
from table_MVC import TableModel
# import pandas as pd

print(f'{time.asctime(time.localtime())}: Start of Loading UI Manipulation Code')


class CallUi(QtWidgets.QMainWindow):
    """[summary]

    Args:
        QtWidgets ([type]): [description]
    """
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # Load DWX Connection Object
        # self.conn_api_mvc = DwxModel()
        self.conn_api, self.conn_api_mvc = asyncio.run(conn_mt())


        # Create Main UI Instance
        self.ui = main_window.Ui_MainWindow()


        #Load Main UI objects
        self.ui.setupUi(self)

        #Generate available symbols from  current MT5 account
        self.symbols = self.conn_api_mvc.GetSymbols(mt5 = self.conn_api)

        #Populate Symbol groups combobox with static list of symbol groups
        self.ui.SYMBOL_GROUPS_COMBOBOX.addItems(self.conn_api_mvc.symbol_groups())
        #Set current index to -1 so that combobox remains empty
        #CurrentIndex is changed to 0 after adding items
        self.ui.SYMBOL_GROUPS_COMBOBOX.setCurrentIndex(-1)

        # Load widget functions (BTN, COMBOBOX) for reacting to actions
        self.setup_btn_connect()
        self.setup_combobox_connect()

        self.load_trades()

        #New Prepared Trade Object
        self.prep_new_trade = None

        #List of Order Buttons. For iterations.
        self.order_btns = (
            self.ui.SELL_BTN, self.ui.SELL_LIMIT_BTN,
            self.ui.BUY_BTN, self.ui.BUY_LIMIT_BTN
        )

        #List of Order Strategy buttons. For iterations
        self.order_strategy_btns = (
            self.ui.SINGLE_TRADE_BTN,
            self.ui.MINIMAL_TRADE_BTN,
            self.ui.TWO_WAY_SPLIT_TRADE_BTN,
            self.ui.THREE_WAY_SPLIT_TRADE_BTN
        )

        #List of Timeframe buttons. For iterations
        self.timeframe_btns = (
            self.ui.MIN_1_BTN,self.ui.MIN_5_BTN,
            self.ui.MIN_15_BTN, self.ui.MIN_30_BTN,
            self.ui.MIN_60_BTN, self.ui.MIN_240_BTN,
            self.ui.MIN_1440_BTN,
        )

        #ist of instrument comboboxes. For iterations
        # self.instr_comboboxes = (
        #     self.ui.CURRENCY_PAIRS_METALS_COMBOBOX, self.ui.COMMS_INDCS_COMBOBOX
        #     )





        #Graphs
        # series = QLineSeries()

        # series.append(0,6)
        # series.append(2,4)
        # series.append(3,8)
        # series.append(6,10)

        # series << QPointF(11,1) << QPointF(13,6) << QPointF(15,6) << QPointF(17,8)

        # chart = QChart()
        # chart.addSeries(series)
        # chart.setAnimationOptions(QChart.SeriesAnimations)
        # chart.setTitle('Line Chart Example')

        # chart.legend().setVisible(True)

        # chart.legend().setAlignment(Qt.AlignBottom)

        # chartview = QChartView(chart)

        # chartview.setRenderHint(QPainter.Antialiasing)

        # self.setCentralWidget(chartview)




        # if self.ui.CURRENT_TRADES_TABLE.selectionChanged():
            # print(True)


        #ADD textlabel function to be loaded, similar to setupBtnconnect
        # also for text edits,
        #writing functions instead of loading in the __init__ will make the code more organized.

        # data = [
        #     [4, 9, 2],
        #     [1, 0, 0],
        #     [3, 5, 0],
        #     [3, 3, 2],
        #     [7, 8, 9],
        # ]

        # data = pd.DataFrame(data)

        # self.table_model = TableModel(data)
        # self.ui.tableView.setModel(self.table_model)
    def load_trades(self):
        """
        _summary_
        """
        trades = self.conn_api_mvc.get_current_trades()
        self.ui.CURRENT_TRADES_TABLE.setModel(TableModel(trades))
        self.ui.CURRENT_TRADES_TABLE \
                .horizontalHeader() \
                .setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)


    def disable_execute_trade_btn(self):
        """Function to disable the Execute Trade button.
        """
        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(False)

    #Change the current text in the alternate combobox to None
    def symbol_groups_combobox_text_changed(self, symbol_group_combobox):
        """_summary_

        Args:
            instr_combobox (combobox Object): Combobox object that created the signal
        """
        #Disable the Execute button.
        self.disable_execute_trade_btn()

        #Check if the symbols combobox has any current symbols, & clear if True 
        if self.ui.SYMBOLS_COMBOBOX:
            self.ui.SYMBOLS_COMBOBOX.clear()

        #Dict matching group symbols to GetSymbols objects
        symbol_groups_dict = {
            'FOREX': self.symbols.forex,
            'METALS': self.symbols.metals,
            'INDICES': self.symbols.indices,
            'COMMODITIES': self.symbols.commodities,
            'ENERGIES': self.symbols.energies,
            'CRYPTO': self.symbols.crypto,
            'FUTURES': self.symbols.futures,
        }

        #While the currentText is not similar to known SYMBOL_GROUPS, return
        if symbol_group_combobox.currentText() not in symbol_groups_dict:
            return

        #Update the symbols combobox with list of the symbols in selected group
        self.ui.SYMBOLS_COMBOBOX.addItems(symbol_groups_dict[symbol_group_combobox.currentText()])
        #Adding items shifts currentIndex to 0
        #Set currentIndex to -1 to keep combobox empty.
        self.ui.SYMBOLS_COMBOBOX.setCurrentIndex(-1)

        print(f'Current Symbol Group to trade: {symbol_group_combobox.currentText()}.')

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

            if order_strategy in \
            [self.ui.MINIMAL_TRADE_BTN, self.ui.SINGLE_TRADE_BTN]:
                pass
            else:
                self.ui.TP_LEVEL_1_LABEL.setEnabled(True)
                self.ui.TP_LEVEL_1_SPINBOX.setEnabled(True)
                self.ui.TP_LEVEL_2_LABEL.setEnabled(True)
                self.ui.TP_LEVEL_2_SPINBOX.setEnabled(True)

                if order_strategy == self.ui.THREE_WAY_SPLIT_TRADE_BTN:
                    self.ui.TP_LEVEL_3_LABEL.setEnabled(True)
                    self.ui.TP_LEVEL_3_SPINBOX.setEnabled(True)


        else: order_strategy.setStyleSheet('')

    def order_timeframe_btn_clicked(self, order_timeframe):
        """[summary]

        Args:
            order_timeframe ([type]): [description]
        """

        #Disable the Execute button.
        self.disable_execute_trade_btn()


        for i in self.timeframe_btns:
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
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(self.conn_api_mvc.get_current_trades)

        # test_hist_req_data = [
        #     {'_symbol': 'EURUSD',
        #     '_timeframe': 1440,
        #     '_start': '2021.01.01 00:00:00',
        #     '_end': pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00') }
        # ]
        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(self.conn_api_mvc.send_hist_request)
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

        self.ui.MIN_1_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_1_BTN)
        )

        self.ui.MIN_5_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_5_BTN)
        )

        self.ui.MIN_15_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_15_BTN)
        )

        self.ui.MIN_30_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_30_BTN)
        )

        self.ui.MIN_60_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_60_BTN)
        )

        self.ui.MIN_240_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_240_BTN)
        )

        self.ui.MIN_1440_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_1440_BTN)
        )


        self.ui.CURRENT_TRADES_TABLE.doubleClicked.connect(self.clicked_table)


    def clicked_table(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        idx = self.ui.CURRENT_TRADES_TABLE.selectedIndexes()[0]
        print(idx)
        id_us = int(self.ui.CURRENT_TRADES_TABLE.model().data(idx,0))
        print(id_us)

        return True

        # self.ui.tableView.setRowCount(5)
        # self.ui.pushButton.clicked.connect(self.myFunction)

    def setup_combobox_connect(self):
        """_summary_
        """
        self.ui.SYMBOL_GROUPS_COMBOBOX.currentTextChanged.connect(
            lambda: self.symbol_groups_combobox_text_changed(self.ui.SYMBOL_GROUPS_COMBOBOX)
        )

    # def setup_combobox_connect(self):
    #     self.ui.TP_LEVEL_spinBox.connect()

    def prepare_new_trade(self):
        """[summary]
        """
        symbols_combobox = self.ui.SYMBOLS_COMBOBOX
        new_trade_dict = {}
        new_trade_dict['symbol_group']=  self.ui.SYMBOL_GROUPS_COMBOBOX.currentText()

        # Risk in ratio form
        new_trade_dict['risk'] = self.ui.RISK_DOUBLESPINBOX.value() / 100



        #Iterate through the order timeframes to find the selected one
        #Do nothing if none is selected
        timeframe = ''
        for i in self.timeframe_btns:
            if i.isChecked():
                timeframe = int(''.join([n for n in i.objectName().split('_') if n.isdigit()]))

                new_trade_dict['timeframe'] = timeframe

        if timeframe == '':
            print('Select an order Timeframe.')
            return


        #Check if the text entered is a valid currency pair that
        # can be operated on ie. existing pairs on the list.
        if symbols_combobox.currentText() not in \
            [symbols_combobox.itemText(i) for i in range(symbols_combobox.count())]:
            print('Selected Symbol is Invalid')
            return

        else:
            symbol = symbols_combobox.currentText()

            new_trade_dict['symbol'] = symbol

        order_type = ''
        #Iterate through the order types to find the selected one
        for i in self.order_btns:
            if i.isChecked():
                order_type = i.text()

                new_trade_dict['order'] = order_type


        if order_type == '':
            print('Select an Order Type.')
            return

        #For orders that are not instant,
        # the price limit/stop needs to be specified as a valid float.
        elif order_type not in ['SELL','BUY']:

            if self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText() != '':
                try:
                    buy_sell_limit = float(self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText())

                    new_trade_dict['buy_sell_limit'] = buy_sell_limit

                except Exception:
                    print('Buy/Sell Limit is not a valid Double value')
                    return
            else:
                print('Order Type requires a specified Price Limit/Stop')
                return


        try:
            self.prep_new_trade = self.conn_api_mvc.prepare_new_trade(new_trade_dict)

            self.ui.PIP_VALUE_TEXT.setText(str(round(self.prep_new_trade.symbol_value, 4)))
            self.ui.ATR_IN_PIPS_TEXT.setText(str(round(self.prep_new_trade.atr_in_points, 2)))
            self.ui.LOT_SIZE_TEXT.setText(str(str(round(self.prep_new_trade.lot_size, 2))))
            self.ui.RISK_AMOUNT_TEXT.setText(str(round(self.prep_new_trade.risk_amount, 4)))
            self.ui.ACCOUNT_BALANCE_TEXT.setText(str(self.prep_new_trade.account_info['balance']))
            self.ui.STOP_LOSS_TEXT.setText(str(round(self.prep_new_trade.stop_loss, 5)))
            self.ui.TAKE_PROFIT_TEXT.setText(str(round(self.prep_new_trade.take_profit, 5)))
            self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(True)

            hist_df = self.prep_new_trade.trade_df

            # hist_table = TableModel(hist_df)

            # model = QtGui.QStandardItemModel()
            # model.setHorizontalHeaderLabels(hist_df.columns)


            self.ui.HIST_DF_TABLE.setVisible(True)
            self.ui.HIST_DF_TABLE.setModel(TableModel(hist_df))



        except Exception:
            traceback.print_exc()



    def execute_new_trade(self):
        """[summary]
        """

        self.ui.EXECUTE_NEW_TRADE_BTN.setEnabled(False)

        trade_strategy = ''
        #iterate to select the trade strategy that is selected.
        #split the trade, or make a single order
        for i in self.order_strategy_btns:
            if i.isChecked():
                trade_strategy = i.text()

        if trade_strategy == '':
            print('Select a trading strategy.')
            return

        for i in self.timeframe_btns:
            if i.isChecked():
                timeframe = int(''.join([n for n in i.objectName().split('_') if n.isdigit()]))

        if timeframe == '':
            print('Select an order Timeframe.')
            return


        try:
            self.conn_api_mvc.new_trade(
                {
                'action': 'OPEN',
                'type': self.prep_new_trade.trade_dict['order'],      #1 for SELL, O for BUY
                'symbol': self.prep_new_trade.symbol,
                #Refers to current price value
                'price': 0.0 if self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText() == '' else\
                     float(self.ui.PRICE_LIMIT_STOP_VALUE.toPlainText()),
                # SL/TP in POINTS, not pips.
                'SL_points':
                    self.prep_new_trade.atr * self.prep_new_trade.sl_multiplier,

                'TP_points':
                    self.prep_new_trade.atr * self.prep_new_trade.tp_multiplier,

                'comment':
                    f'{str(timeframe)}_{self.ui.NEW_TRADE_COMMENT_VALUE.toPlainText()}',
                    
                'volume': round(self.prep_new_trade.lot_size, 2),
                'magic': 123456,
                'ticket': 0
                },
                {
                    'trade_strategy': trade_strategy,
                    'timeframe': timeframe,
                    'split_ratio': 0.9,
                    'split_ratio_2' : 0.5,
                    'tp_multiplier_1' : self.ui.TP_LEVEL_1_SPINBOX.value(),
                    'tp_multiplier_2' : self.ui.TP_LEVEL_2_SPINBOX.value(),
                    'tp_multiplier_3' : self.ui.TP_LEVEL_3_SPINBOX.value()
                },
            )
        except Exception:
            traceback.print_exc()


def setup_window():
    """
    Initialize app window
    """
    app = QtWidgets.QApplication(sys.argv)
    now_window = CallUi()
    # print(time.asctime(time.localtime()))
    print(f"{time.asctime(time.localtime())}: Finished loading App GUI")
    now_window.show()
    sys.exit(app.exec_())
