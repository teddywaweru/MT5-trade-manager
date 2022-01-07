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
    def send_hist_request(self, hist_dict_request ):
        if len(hist_dict_request) == 0:
            return print('Empty Request.')
        for request in hist_dict_request:
            _symbol = request.get('_symbol', 'EURGBP')
            #A00 Change timestamp from daily.
            _timestamp = request.get('_timestamp', 1440)
            _start = request.get('_start', '2022.01.01 00.00.00')
            _end = request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H.%M.00'))
            #check whether the item has valid data
            #is pair valid
            # is timeframe int? otherwise show 15 min data. Or other default value?
            # Automatically select start period? No. Should be provided, but automatically selected in the application.
            #end time would always be now.
            self.ZMQ_._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timestamp, _start, _end)
            time.sleep(0.0005)

        #Push collected data to data manipulation to prepare DataFrames that may be utilised at any time
        for request in hist_dict_request:
            
            #create the label in the History_DB keys
            #A00 change timestamp. add try except loops
            hist_db_key = self.generate_hist_db_key(request['_symbol'], request.get('_timestamp', 1440))
            
            #Create data manipulation object for basic Data Wrangling
            #Returns DataFrame with OHLC & atr
            data_wrang = data_manipulation(self.ZMQ_._History_DB[hist_db_key])



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
    def prepare_new_trade(self):
        print(time.time())
        _symbol = 'EURGBP'
        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        self.ZMQ_._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        time.sleep(5)

        #Generate History DB Key based on symbol & timeframe
        #A00 Change code to work for various timeframes.
        hist_db_key = self.generate_hist_db_key(_symbol, 1440)

        #Create DataFrame object from data collected fron Historical Data
        new_trade_df = data_manipulation(self.ZMQ_._History_DB[hist_db_key])

        #Obtain Recent Account Information. Account Balance is most critical
        #A00 Code may change when account info is stored in its own dict. For now, this is collected from the thread data output dict.
        self.ZMQ_._DWX_MTX_GET_ACCOUNT_INFO_()
        time.sleep(0.5)
        account_info = self.ZMQ_._thread_data_output

        #Initiate  Risk Management Class
        # account balance
        # symbol
        new_trade = risk_management(self.ZMQ_, 0.02, account_info, new_trade_df.data_df, hist_db_key)

        trade = new_trade.calc_lot()

        print(trade.SL)
        time.time()

        # To calculate Pip Value per Trade, the symbol has to be compared against the USD exchange value since this is the current account currency
        # If the USD is not in the 
        # if 'USD' not in _symbol:


        # Symbol against USD if USD not in _symbol
        # ATR Value



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

