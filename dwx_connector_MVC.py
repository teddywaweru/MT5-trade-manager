import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot, Qt
from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
from data_manipulation import data_manipulation
from risk_management import risk_management
import pandas as pd
import time

class DwxModel():

    def __init__(self):
        self.ZMQ_ = dwx()
        #to select periods in minutes as MT4 formats
        self.periods = {
                1: 'M1', 5 : 'M5', 15 : 'M15', 30 : 'M30', 60 : 'H1',
                240 : 'H4', 1440 : 'D1', 10080 : 'W1'
            }
        
        
        
    @Slot()
    def say_hello():
        print('Button Press recognized.')



    @Slot()
    def subscribe_marketdata(self, list_of_pairs = ['AUDCAD']):
        for pair in list_of_pairs:
            #subscribe to Pairs in List
            self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(pair)
            # print('Subscribed to {}'.format(pair))


    @Slot()
    def send_hist_request(self, hist_request ):
        if hist_request == {}:
            return print('Empty Request.')
        
        _symbol = hist_request.get('_symbol', 'USDJPY')
        #A00 Change timestamp from daily.
        _timeframe = hist_request.get('_timeframe', 1440)
        _start = hist_request.get('_start', '2022.01.01 00.00.00')
        _end = hist_request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H.%M.00'))
        #check whether the item has valid data
        #is pair valid
        # is timeframe int? otherwise show 15 min data. Or other default value?
        # Automatically select start period? No. Should be provided, but automatically selected in the application.
        #end time would always be now.
        self.ZMQ_._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timeframe, _start, _end)
        time.sleep(1)

        #Push collected data to data manipulation to prepare DataFrames that may be utilised at any time
        #ADD able to add multiple requests???
            #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = self.generate_hist_db_key(hist_request['_symbol'], hist_request.get('_timeframe', 1440))
        
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = data_manipulation(self.ZMQ_._History_DB[hist_db_key]).data_df

        return hist_db_key, hist_db_df



    # Close all trades
    @Slot()
    def close_all_trades(self):
        self.ZMQ_._DWX_MTX_CLOSE_ALL_TRADES_()

    # Open New Trade
    @Slot()
    def new_trade(self):
        self.ZMQ_._DWX_MTX_NEW_TRADE_()

    # Get all open trades
    @Slot()
    def get_trades(self):
        # ZMQ_ = dwx()
        self.ZMQ_._DWX_MTX_GET_ALL_OPEN_TRADES_()

    # Prepare New Trade. Involves calculating all necessary parameters for the order.
    # These form the default values that may then be changed/edited manually.
    @Slot()
    def prepare_new_trade(self, new_trade_dict):
        
        #Dummy Data for testing
        new_trade_dict['_start'] = '2021.12.01 00.00.00'
        new_trade_dict['_end'] = pd.Timestamp.now().strftime('%Y.%m.%d %H.%M.00')
        
        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        # self.ZMQ_._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)

        #Generate History DB Key based on symbol & timeframe
        #A00 Change code to work for various timeframes.
        # hist_db_key = self.generate_hist_db_key(_symbol, 1440)

        #Create DataFrame object from data collected fron Historical Data
        # trade_hist_df = data_manipulation(self.ZMQ_._History_DB[hist_db_key])

        #Obtain Recent Account Information. Account Balance is most critical
        #A00 Code may change when account info is stored in its own dict. For now, this is collected from the thread data output dict.
        self.ZMQ_._DWX_MTX_GET_ACCOUNT_INFO_()
        time.sleep(1)
        account_info = self.ZMQ_._thread_data_output

        #Initiate  Risk Management Class
        # account balance
        # symbol
        new_trade = risk_management(self.ZMQ_,
                                        new_trade_dict['_order'],
                                        0.01,
                                        account_info['_data'][-1],
                                        trade_hist_df,
                                        hist_db_key)
        new_trade.calc_lot()
        return new_trade




    # Open New Trade
    # @Slot()
    # def new_trade(self, _symbol):
    #     new_trade = money_management(self.ZMQ_)
    #     self._type = 
    #     self._symbol = 
    #     self._price = 
    #     self._SL = new_trade.calc_SL()
    #     self._comment = new_trade.calc_TP() 
    #     self._lots = new_trade.calc_lot()
    #     self._magic = 
    #     self._ticket = 
        
        #Set SL, TP, Margins, 

        #Update Trailing Stop
        # Calculate current  ATR & difference from buying cost

    # Create History Label
    def generate_hist_db_key(self, _symbol, _timeframe):
        hist_db_key = '' + _symbol + '_' + str(self.periods[_timeframe])
        return hist_db_key

        #A00 Clear historical DB

