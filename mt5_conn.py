"""
_summary_
"""
# pylint: disable=eval-used

# import MetaTrader5 as mt5
import pandas as pd

from math import ceil

import time

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

        time.sleep(0.5)


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


    def new_trade(self, new_trade, modif_trade):
        """_summary_

        Args:
            new_trade (_type_): _description_
            modif_trade (_type_): _description_
        """

        #MT5 API has different definitions for some of the dict parameters for a
        # new trade, which shall be changed

        trade_action = '{}.{}'.format(MT5_OBJ_STRING, MT5_TRADE_ACTIONS['instant'])\
                            if new_trade['_price'] == 0 else \
                            '{}.{}'.format(MT5_OBJ_STRING, MT5_TRADE_ACTIONS['pending'])

        trade_type = '{}.{}'.format(MT5_OBJ_STRING, MT5_ORDER_TYPES[new_trade['_type']])

        symbol_info = self.mt5_mvc.symbol_info(new_trade['_symbol'])._asdict()

        type_filling = '{}.{}'.format(MT5_OBJ_STRING, MT5_ORDER_TYPE_FILLING[symbol_info['filling_mode']])

        new_trade.update(
            {
                'action': eval(trade_action),

                'symbol': new_trade['_symbol'],

                'volume': new_trade['_lots'],

                'type': eval(trade_type),

                'price': symbol_info['ask'],

                # 'sl': 100,
                'sl': symbol_info['ask'] + new_trade['_SL'] * symbol_info['point'],

                # 'tp': 100,
                'tp': symbol_info['ask'] - new_trade['_TP'] * symbol_info['point'],

                'deviation': 20,

                # 'type_filling': eval('{}.ORDER_FILLING_RETURN'.format(MT5_OBJ_STRING)),
                'type_filling': eval(type_filling),

                # 'type_time': eval('{}.ORDER_TIME_GTC'.format(MT5_OBJ_STRING)),
                # 'type_time': symbol_info['start_time'],
                # 'type_time': 1,

                # 'expiration': symbol_info['expiration_time']

            }
        )
        remove_keys= ['_action', '_type', '_symbol', '_price', '_SL',\
             '_TP', '_comment', '_magic', '_ticket','_lots']

        [new_trade.pop(key, None) for key in remove_keys]

        if modif_trade['trade_strategy'] == 'SINGLE TRADE':
            self.mt5_mvc.order_send(new_trade)

        elif modif_trade['trade_strategy'] == '2-WAY SPLIT TRADE':
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade
            new_trade_1.update(
                {'volume': ceil((new_trade['volume'] * modif_trade['split_ratio'] *100))/100,}
            )

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2.update(
                {'volume': new_trade['volume'] - new_trade_1['volume'],
                'tp': new_trade['tp'] * 5}

            )


            for i in [
                new_trade_1, new_trade_2
            ]:
                result = self.mt5_mvc.order_send(i)
                print(result.retcode)
                print(self.mt5_mvc.last_error())
                print(result._asdict().items())
                time.sleep(0.1)


        elif modif_trade['trade_strategy'] == '3-WAY SPLIT TRADE':
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade (0.8)
            new_trade_1.update(
                {'volume': new_trade['volume'] * modif_trade['split_ratio'],}

            )

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2.update(
                {
                    'volume': new_trade['volume'] * (1 - modif_trade['split_ratio']) * modif_trade['split_ratio_2'],
                    'tp': new_trade['tp'] * 3
                }
            )

            new_trade_3 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_3.update(
                {
                    'volume': new_trade['volume'] - new_trade_1['volume'] - new_trade_2['volume'],
                    'tp': new_trade['tp'] * 5
                }
            )


            for i in [
                new_trade_1, new_trade_2, new_trade_3
            ]:
                self.mt5_mvc.order_send(i)
                time.sleep(0.1)

        elif modif_trade['trade_strategy'] == 'MINIMAL TRADE':
            new_trade.update(
                {
                    'volume': new_trade['volume'] * 0.2     #Trade @ 40% of the Previous Risk Amount
                }
            )

            self.mt5_mvc.order_send(new_trade)



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

#MT5 Actions
MT5_TRADE_ACTIONS = {
    'instant':'TRADE_ACTION_DEAL',
    'pending': 'TRADE_ACTION_PENDING',
    'change_sltp': 'TRADE _ACTION_SLTP',
    'modify': 'TRADE_ACTION_MODIFY',
    'remove': 'TRADE_ACTION_REMOVE',
    'close_opp': 'TRADE_ACTION_CLOSE_BY'
}

#MT5 Order Types
MT5_ORDER_TYPES = {
    'BUY': 'ORDER_TYPE_BUY',
    'SELL': 'ORDER_TYPE_SELL',
    'BUY LIMIT': 'ORDER_TYPE_BUY_LIMIT',
    'SELL LIMIT': 'ORDER_TYPE_SELL_LIMIT',
    'BUY STOP LIMIT': 'ORDER_TYPE_BUY_STOP_LIMIT',
    'SELL STOP LIMIT': 'ORDER_TYPE_SELL_STOP_LIMIT',
    'CLOSE OPP': 'ORDER_TYPE_CLOSE_BY'
}

MT5_ORDER_TYPE_FILLING = {
    1: 'ORDER_FILLING_FOK',
    2: 'ORDER_FILLING_IOC',
    3: 'ORDER_FILLING_RETURN',

}
