"""[summary]

Returns:
    [type]: [description]
"""

import time
from PySide6.QtCore import Slot, Qt
# import sys
# from PyQt5 import QtCore, QtGui, QtWidgets
from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
from data_manipulation import DataManipulation
from risk_management import RiskManagement
import pandas as pd


class DwxModel():
    """[summary]
    """
    def __init__(self):
        self.zmq_dwx = dwx()
        #to select periods in minutes as MT4 formats
        self.periods = {
                1: 'M1', 5 : 'M5', 15 : 'M15', 30 : 'M30', 60 : 'H1',
                240 : 'H4', 1440 : 'D1', 10080 : 'W1'
            }



    @Slot()
    def subscribe_marketdata(self, list_of_pairs):
        """[summary]

        Args:
            list_of_pairs (list, optional): [description]. Defaults to ['AUDCAD'].
        """
        for pair in list_of_pairs:
            #subscribe to Pairs in List
            self.zmq_dwx._DWX_MTX_SUBSCRIBE_MARKETDATA_(pair)
            # print('Subscribed to {}'.format(pair))


    @Slot()
    def send_hist_request(self, hist_request ):
        """[summary]

        Args:
            hist_request ([type]): [description]
        Returns:
            [type]: [description]
        """
        if hist_request == {}:
            return print('Empty Request.')
        
        _symbol = hist_request.get('_symbol', 'USDJPY')
        #A00 Change timestamp from daily.
        _timeframe = hist_request.get('_timeframe', 1440)           #Default to daily timeframe
        _start = hist_request.get('_start', '2022.02.08 08:45')
        _end = hist_request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H:%M'))
        #check whether the item has valid data
        #is pair valid
        # is timeframe int? otherwise show 15 min data. Or other default value?
        # Automatically select start period?
        # No. Should be provided, but automatically selected in the application.
        #end time would always be now.
        self.zmq_dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timeframe, _start, _end)
        time.sleep(0.05)

        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time
        #ADD able to add multiple requests???
        #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = self.generate_hist_db_key(hist_request['_symbol'],
                                        hist_request.get('_timeframe', 1440)
                                        )
        
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = DataManipulation(self.zmq_dwx._History_DB[hist_db_key]).data_df

        return hist_db_key, hist_db_df



    # Close all trades
    @Slot()
    def close_all_trades(self):
        """[summary]
        """
        self.zmq_dwx._DWX_MTX_CLOSE_ALL_TRADES_()

    # Open New Trade
    @Slot()
    def new_trade(self, new_trade, modif_trade):
        """[summary]

        Args:
            new_trade_dict ([type]): [description]
            modify_dict ([type]): [description]
        """
        if modif_trade['trade_strategy'] == 'SINGLE TRADE':
            self.zmq_dwx._DWX_MTX_NEW_TRADE_(new_trade)

        elif modif_trade['trade_strategy'] == 'SPLIT TRADE':
            new_trade_1 = new_trade.copy()
            new_trade_1.update(
                {'_lots': new_trade['_lots'] * modif_trade['split_ratio']}
            )

            new_trade_2 = new_trade.copy()
            new_trade_2.update(
                {'_lots': new_trade['_lots'] * modif_trade['split_ratio'],
                '_TP': new_trade['_TP'] * 2}
            )


            for i in [
                new_trade_1, new_trade_2
            ]:
                self.zmq_dwx._DWX_MTX_NEW_TRADE_(i)
                time.sleep(0.5)

        elif modif_trade['trade_strategy'] == 'MINIMAL TRADE':
            new_trade.update(
                {
                    '_lots': new_trade['_lots'] * 0.4,      #Trade @ 40% of the Previous Risk Amount
                    '_SL': new_trade['_SL'] * 2,            #Update stop Loss. Arbitrarily selected as 2*x
                    '_TP': new_trade['_TP'] * 2             #Update Tae Profit. Arbitrarily selected as 2*x
                }
            )

            self.zmq_dwx._DWX_MTX_NEW_TRADE_(new_trade)

    # Get all open trades
    @Slot()
    def get_trades(self):
        """[summary]
        """
        # zmq_dwx = dwx()
        self.zmq_dwx._DWX_MTX_GET_ALL_OPEN_TRADES_()

    # Prepare New Trade. Involves calculating all necessary parameters for the order.
    # These form the default values that may then be changed/edited manually.
    @Slot()
    def prepare_new_trade(self, new_trade_dict):
        """[summary]

        Args:
            new_trade_dict ([Parameters]): [Parameters of a new trade received from the User]

        Returns:
            [Trade Thresholds]: [Aspects of the new trade received from Risk Mangement Calculations]
        """
        #Dummy Data for testing
        #Data duration statically selected to be set to be at least 30 data points from current time
        new_trade_dict['_start'] = (
            pd.Timestamp.now() - pd.Timedelta(minutes = (new_trade_dict['_timeframe'] * 30))).strftime('%Y.%m.%d %H:%M:00')

        new_trade_dict['_end'] = pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00')
        
        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        # self.zmq_dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)

        #Generate History DB Key based on symbol & timeframe
        #A00 Change code to work for various timeframes.
        # hist_db_key = self.generate_hist_db_key(_symbol, 1440)

        #Obtain Recent Account Information. Account Balance is most critical
        #A00 Code may change when account info is stored in its own dict.
        # For now, this is collected from the thread data output dict.
        self.zmq_dwx._DWX_MTX_GET_ACCOUNT_INFO_()
        time.sleep(0.03)
        account_info = self.zmq_dwx._thread_data_output

        #Initiate  Risk Management Class
        # account balance
        # symbol
        new_trade = RiskManagement(self.zmq_dwx,
                                        new_trade_dict['_order'],   #order type
                                        0.005,                      # Percentage risk of account
                                        account_info['_data'][-1],
                                        trade_hist_df,
                                        hist_db_key)
        new_trade.calc_lot()
        return new_trade

    # Create History Label
    def generate_hist_db_key(self, _symbol, _timeframe):
        """[summary]

        Args:
            _symbol ([type]): [description]
            _timeframe ([type]): [description]

        Returns:
            [type]: [description]
        """
        hist_db_key = '' + _symbol + '_' + str(self.periods[_timeframe])
        return hist_db_key


        #A00 Clear historical DB

