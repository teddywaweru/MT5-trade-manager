"""
_summary_
"""
# pylint: disable=eval-used

# import MetaTrader5 as mt5
import pandas as pd

from data_manipulation import DataManipulation

from risk_management import RiskManagement


class Mt5Mvc():
    """_summary_
    """

    def __init__(self, mt5 = None):
        """_summary_
        """
        self.mt5_mvc = mt5

        self.periods = TIMEFRAMES_PERIODS

        self.curr_mtl_pairs = CURRENCY_METAL_PAIRS

        self.comm_indcs = COMMODITIES_INDICES

        # calculations from RiskManagement class
        self.new_trade_risk = None


    def prepare_new_trade(self,new_trade_dict):
        """_summary_
        """

        #Data duration statically selected to be set to be at least 30 data points from current time
        new_trade_dict['_start'] = (
            pd.Timestamp.now() - pd.Timedelta(minutes = (new_trade_dict['_timeframe'] * 30)))

        new_trade_dict['_end'] = pd.Timestamp.now()

        new_trade_dict['instr_type'] = 'curr_mtl' if new_trade_dict['_symbol'] in self.curr_mtl_pairs \
                                    else 'comm_indcs' if new_trade_dict['_symbol'] in self.comm_indcs \
                                    else None

        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        # self.dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)

        #Obtain Recent Account Information. Account Balance is most critical
        account_info = self.mt5_mvc.account_info()._asdict()

        #Initiate  Risk Management Class
        # account balance
        # symbol
        self.new_trade_risk = RiskManagement(self.mt5_mvc,
                                        new_trade_dict,             # New Trade details
                                        0.0095,                      # Percentage risk of account
                                        account_info,
                                        trade_hist_df,
                                        hist_db_key)

        self.new_trade_risk.calc_lot()
        return self.new_trade_risk



    def send_hist_request(self,hist_request):
        """_summary_
        """
        if hist_request == {}:
            return print('Empty Request.')

        _symbol = hist_request.get('_symbol', 'EURUSD')
        #A00 Change timestamp from daily.
        # MT5 Functionality, requires the timeframe to be stated as self.mt5_mvc.TIMEFRAME_M15
        _timeframe = '{}.{}'.format(MT5_OBJ_STRING,
                                        TIMEFRAMES_PERIODS[hist_request.get('_timeframe', 1440)])

        #ADD able to add multiple requests???
        #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = '{}_{}'.format(hist_request['_symbol'],
                                    TIMEFRAMES_PERIODS[hist_request['_timeframe']])
        _start = hist_request.get('_start', None)
        _end = hist_request.get('_end',pd.Timestamp.now())

        #Get historical rates for the _symbol
        hist_rates = self.mt5_mvc.copy_rates_range(_symbol, eval(_timeframe), _start, _end)

        hist_db_df = pd.DataFrame(hist_rates)

        hist_db_df['time'] = pd.to_datetime(hist_db_df['time'], unit= 's')

        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = DataManipulation(hist_db_df).data_df

        return hist_db_key, hist_db_df

    def get_trades(self):
        pass



        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time

TIMEFRAMES_PERIODS = {
                1: 'TIMEFRAME_M1', 5 : 'TIMEFRAME_M5', 15 : 'TIMEFRAME_M15',
                30 : 'TIMEFRAME_M30', 60 : 'TIMEFRAME_H1', 240 : 'TIMEFRAME_H4',
                1440 : 'TIMEFRAME_D1', 10080 : 'TIMEFRAME_W1'
                }

CURRENCY_METAL_PAIRS = (
                'AUDCAD', 'AUDCHF','AUDJPY', 'AUDNZD', 'AUDSGD','AUDUSD',
                'CADCHF','CADJPY',
                'CHFJPY','CHFSGD',
                'EURAUD','EURCAD','EURCHF', 'EURGBP', 'EURJPY',\
                    'EURNZD', 'EURSGD', 'EURUSD',
                'GBPAUD','GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPNZD',\
                    'GBPSGD', 'GBPUSD',
                'NOKSEK',
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

# MT5 Syntax requires instances where a string is required for eval() functions
MT5_OBJ_STRING = 'self.mt5_mvc'

