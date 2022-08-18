"""[summary]

Returns:
    [type]: [description]
"""


# from os.path import exists
import time
from math import ceil
# from PySide6.QtCore import Slot, Qt
# import sys

#DWX Connector method - dwx_zmq, or dwx_connect
# from dwx_connector import connect_dwx

# from PyQt5 import QtCore, QtGui, QtWidgets
#DWX_ZeroMQ Connector
# from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx_zmq

#DWXConnect API
# from dwx_connect.api.dwx_client import dwx_client as dwx_conn
from data_manipulation import DataManipulation
from risk_management import RiskManagement
import pandas as pd


class DwxZmqModel():
    """[summary]
    """
    def __init__(self, dwx = None):

        # self.dwx = connect_dwx()
        self.dwx = dwx
        
        #to select periods in minutes as MT4 formats
        self.periods = TIMEFRAMES_PERIODS
        self.curr_mtl_pairs = CURRENCY_METAL_PAIRS

        self.comm_indcs = COMMODITIES_INDICES

        # calculations from RiskManagement class
        self.new_trade_risk = None



    # @Slot()
    def subscribe_marketdata(self, list_of_pairs):
        """[summary]

        Args:
            list_of_pairs (list, optional): [description]. Defaults to ['AUDCAD'].
        """
        for pair in list_of_pairs:
            #subscribe to Pairs in List
            self.dwx._DWX_MTX_SUBSCRIBE_MARKETDATA_(pair)
            print('Subscribed to {}'.format(pair))


    # @Slot()
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

        #ADD able to add multiple requests???
        #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = '{}_{}'.format(hist_request['_symbol'],
                                    TIMEFRAMES_PERIODS[hist_request['_timeframe']])
        _start = hist_request.get('_start', '2022.02.08 08:45')
        _end = hist_request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H:%M'))

        self.dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timeframe, _start, _end)
        time.sleep(0.5)


        if len(self.dwx._History_DB[hist_db_key]) <20:
            _start =(
                pd.Timestamp.now() - pd.Timedelta(minutes = (hist_request['_timeframe'] * 200))).strftime('%Y.%m.%d %H:%M:00')

            self.dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timeframe, _start, _end)
            time.sleep(0.5)


        
        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = DataManipulation(self.dwx._History_DB[hist_db_key]).data_df

        return hist_db_key, hist_db_df


    def get_current_trades(self):
        pass

    # Close all trades
    # @Slot()
    def close_all_trades(self):
        """[summary]
        """
        self.dwx._DWX_MTX_CLOSE_ALL_TRADES_()

    # Open New Trade
    # @Slot()
    def new_trade(self, new_trade, modif_trade):
        """[summary]

        Args:
            new_trade_dict ([type]): [description]
            modify_dict ([type]): [description]
        """
        #Convert order type to MT4 Format
        new_trade['_type'] = MT4_ORDER_TYPE[new_trade['_type']]
        
        if modif_trade['trade_strategy'] == 'SINGLE TRADE':
            self.dwx._DWX_MTX_NEW_TRADE_(new_trade)

        elif modif_trade['trade_strategy'] == '2-WAY SPLIT TRADE':
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade
            new_trade_1.update(
                {'_lots': ceil((new_trade['_lots'] * modif_trade['split_ratio'] *10))/10,}
                
            )

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2.update(
                {'_lots': new_trade['_lots'] - new_trade_1['_lots'],
                '_TP': new_trade['_TP'] * 5}
            )


            for i in [
                new_trade_1, new_trade_2
            ]:
                self.dwx._DWX_MTX_NEW_TRADE_(i)
                time.sleep(0.1)


        elif modif_trade['trade_strategy'] == '3-WAY SPLIT TRADE':
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade (0.8)
            new_trade_1.update(
                {'_lots': new_trade['_lots'] * modif_trade['split_ratio'],}
                
            )

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2.update(
                {
                    '_lots': new_trade['_lots'] * (1 - modif_trade['split_ratio']) * modif_trade['split_ratio_2'],
                    '_TP': new_trade['_TP'] * 3
                }
            )

            new_trade_3 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_3.update(
                {
                    '_lots': new_trade['_lots'] - new_trade_1['_lots'] - new_trade_2['_lots'],
                    '_TP': new_trade['_TP'] * 5
                }
            )


            for i in [
                new_trade_1, new_trade_2, new_trade_3
            ]:
                self.dwx._DWX_MTX_NEW_TRADE_(i)
                time.sleep(0.1)

        elif modif_trade['trade_strategy'] == 'MINIMAL TRADE':
            new_trade.update(
                {
                    '_lots': new_trade['_lots'] * 0.2     #Trade @ 40% of the Previous Risk Amount
                }
            )

            self.dwx._DWX_MTX_NEW_TRADE_(new_trade)

    # Get all open trades
    # @Slot()
    def get_trades(self):
        """[summary]
        """
        # dwx = dwx()
        self.dwx._DWX_MTX_GET_ALL_OPEN_TRADES_()

    # Prepare New Trade. Involves calculating all necessary parameters for the order.
    # These form the default values that may then be changed/edited manually.
    # @Slot()
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
            pd.Timestamp.now() - pd.Timedelta(minutes = (new_trade_dict['_timeframe'] * 72))).strftime('%Y.%m.%d %H:%M:00')

        new_trade_dict['_end'] = pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00')

        new_trade_dict['instr_type'] = 'curr_mtl' if new_trade_dict['_symbol'] in self.curr_mtl_pairs \
                                    else 'comm_indcs' if new_trade_dict['_symbol'] in self.comm_indcs \
                                    else None
        
        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        #Generate History DB Key based on symbol & timeframe
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)


        #Obtain Recent Account Information. Account Balance is most critical
        #A00 Code may change when account info is stored in its own dict.
        # For now, this is collected from the thread data output dict.
        self.dwx._DWX_MTX_GET_ACCOUNT_INFO_()
        time.sleep(1)
        account_info = self.dwx._thread_data_output

        #Initiate  Risk Management Class
        # account balance
        # symbol
        self.new_trade_risk = RiskManagement(self.dwx,
                                        new_trade_dict,             # New Trade details
                                        account_info['_data'][-1],
                                        trade_hist_df,
                                        hist_db_key)

        self.new_trade_risk.calc_lot()
        return self.new_trade_risk

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



class DwxConnModel():
    """_summary_
    """

    def __init__(self, dwx = None):

        self.dwx = dwx

        self.periods = TIMEFRAMES_PERIODS

        self.new_trade_risk = None

        # self.curr_mtl_pairs = CURRENCY_METAL_PAIRS

        # self.comm_indcs = COMMODITIES_INDICES
    





    def get_current_trades(self):
        pass

    
    #Subscribe to list of trading instruments
    # @Slot()
    def subscribe_marketdata(self, list_of_pairs):
        """_summary_

        Args:
            list_of_pairs (_type_): _description_
        """
        for pair in list_of_pairs:
            pass

    #Close all active trades
    # @Slot()
    def close_all_trades(self):
        """_summary_
        """        

        pass


    # Get all open trades
    # @Slot()
    def get_trades(self):
        """_summary_
        """        

        pass


    # Prepare New Trade. Involves calculating all necessary parameters for the order.
    # These form the default values that may then be changed/edited manually.
    # @Slot()
    def prepare_new_trade(self, new_trade_dict):
        """_summary_

        Args:
            new_trade_dict (_type_): _description_
        """
        #Dummy Data for testing
        #Data duration statically selected to be set to be at least 30 data points from current time
        new_trade_dict['_start'] = (
            pd.Timestamp.now() - pd.Timedelta(minutes = (new_trade_dict['_timeframe'] * 30))).strftime('%Y.%m.%d %H:%M:00')

        new_trade_dict['_end'] = pd.Timestamp.now().strftime('%Y.%m.%d %H:%M:00')

        new_trade_dict['instr_type'] = 'curr_mtl' if new_trade_dict['_symbol'] in self.curr_mtl_pairs \
                                    else 'comm_indcs' if new_trade_dict['_symbol'] in self.comm_indcs \
                                    else None
        
        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        # self.dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)

        #Generate History DB Key based on symbol & timeframe
        #A00 Change code to work for various timeframes.
        # hist_db_key = self.generate_hist_db_key(_symbol, 1440)

        #Obtain Recent Account Information. Account Balance is most critical
        #A00 Code may change when account info is stored in its own dict.
        # For now, this is collected from the thread data output dict.
        
        # time.sleep(0.3)
        account_info = self.dwx.account_info

        #Initiate  Risk Management Class
        # account balance
        # symbol
        self.new_trade_risk = RiskManagement(self.dwx,
                                        new_trade_dict,             # New Trade details
                                        0.0095,                      # Percentage risk of account
                                        account_info,
                                        trade_hist_df,
                                        hist_db_key)
        self.new_trade_risk.calc_lot()

        return self.new_trade_risk


    # @Slot()
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
        _start = pd.Timestamp(hist_request.get('_start', '2022.02.08 08:45')).timestamp()
        _end = pd.Timestamp(hist_request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H:%M'))).timestamp()

        # _date = int((datetime.utcnow() - timedelta(days=30)).timestamp())
        #check whether the item has valid data
        #is pair valid
        # is timeframe int? otherwise show 15 min data. Or other default value?
        # Automatically select start period?
        # No. Should be provided, but automatically selected in the application.
        #end time would always be now.
        self.dwx.get_historic_data(
            symbol= _symbol,
            time_frame=TIMEFRAMES_PERIODS[_timeframe],
            start= _start,
            end= _end
        )
        
        time.sleep(5)


        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time
        #ADD able to add multiple requests???
        #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = '{}_{}'.format(_symbol, TIMEFRAMES_PERIODS[_timeframe])
        
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = DataManipulation(self.dwx.historic_data[hist_db_key]).data_df
            

        return hist_db_key, hist_db_df








###############################################

# DECLARATION OF GLOBAL VARIABLES FOR THE CLASSES ABOVE

###############################################



TIMEFRAMES_PERIODS = {
                1: 'M1', 5 : 'M5', 15 : 'M15', 30 : 'M30', 60 : 'H1',
                240 : 'H4', 1440 : 'D1', 10080 : 'W1'
                }

CURRENCY_METAL_PAIRS = (
                'AUDCAD', 'AUDCHF','AUDJPY', 'AUDNZD', 'AUDSGD','AUDUSD',
                'CADCHF','CADJPY',
                'CHFJPY','CHFSGD',
                'EURAUD','EURCAD','EURCHF', 'EURGBP', 'EURJPY',\
                    'EURNZD', 'EURSGD', 'EURUSD',
                'GBPAUD','GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPNOK', 'GBPNZD', 'GBPSEK',\
                    'GBPSGD', 'GBPUSD',
                'NOKSEK', 'NOKJPY',
                'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD',
                'SEKJPY',
                'SGDJPY',
                'USDCAD', 'USDCHF', 'USDCNH', 'USDJPY', 'USDSGD', 'USDTHB', 'USDZAR',
                'XAGUSD', 'XAUUSD', 'XPDUSD', 'XPTUSD'
                )

COMMODITIES_INDICES = (
                'AUS200', 'CHINAH', 'CN50', 'FRA40', 'HK50', 'NAS100',
                'GER40', 'GERTEC30', 'NETH25', 'SCI25', 'SPA35','UK100',
                'US30', 'US500', 'US2000', 'USDX',
                'SpotCrude', 'Cattle', 'Cotton', 'Copper', 'OrangeJuice',
                'Soybeans', 'SpotBrent'
                )

MT4_ORDER_TYPE = {
            'SELL': 1, 'BUY': 0, 'BUY LIMIT': 2, 'SELL LIMIT': 3, 
        }
