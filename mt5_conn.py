"""
_summary_
"""
# pylint: disable=eval-used

import time
from math import ceil
print(f'{time.asctime(time.localtime())}: Start loading pandas')
# import pandas as pd
from pandas import Timestamp, Timedelta, DataFrame, to_datetime
print(f'{time.asctime(time.localtime())}: Finish loading pandas')

# from dataclasses import dataclass

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

        # Parameter calculations from RiskManagement class
        self.trade_risk_calc = None

    def symbol_groups(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return ['FOREX', 'METALS', 'INDICES', 'COMMODITIES', \
            'CRYPTO', 'ENERGIES', 'FUTURES']



    class GetSymbols:
        """_summary_

        Returns:
            _type_: _description_
        """
        def __init__(self, mt5= None):
            """_summary_
            """
            self.mt5 = mt5

            def segment_symbols(text):
                """_summary_
                """
                return sorted((i._asdict()['name']for i in symbols_info \
                    if text in i._asdict()['path'].lower() \
                        and i._asdict()['trade_mode'] == 4))
                        #Trade_mode=4 refers to symbols that have no trade restrictions
                        # https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants#:~:text=of%20enumeration%20ENUM_SYMBOL_TRADE_MODE.-,ENUM_SYMBOL_TRADE_MODE,-Identifier

            print(f"{time.asctime(time.localtime())}: Start Loading Symbols")
            symbols_info = self.mt5.symbols_get()


            self.forex = segment_symbols('forex')
            self.metals = segment_symbols('metals')
            self.indices = segment_symbols('indices')
            self.stocks =  segment_symbols('stocks')
            self.commodities =  segment_symbols('commodities')
            self.crypto = segment_symbols('crypto')
            self.energies = segment_symbols('energies')
            self.futures = segment_symbols('futures')

            print(f"{time.asctime(time.localtime())}: Finish Loading Symbols")



    def get_current_trades(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        open_positions = self.mt5_mvc.positions_get()

        open_positions_list = [i._asdict() for i in open_positions]

        open_positions_df = DataFrame(open_positions_list)

        return open_positions_df


    def prepare_new_trade(self,new_trade_dict):
        """_summary_
        """

        #Data duration statically selected to be set to be at least 30 data points from current time
        new_trade_dict['start'] = (
            Timestamp.now() - Timedelta(minutes = (new_trade_dict['timeframe'] * 30)))

        new_trade_dict['end'] = Timestamp.now()

        new_trade_dict['instr_type'] = 'curr_mtl' if new_trade_dict['symbol'] in self.curr_mtl_pairs \
                                    else 'comm_indcs' if new_trade_dict['symbol'] in self.comm_indcs \
                                    else None

        # Update History_DB. Daily Data selected by default.
        #A00 Change code to work for various timeframes.
        # self.dwx._DWX_MTX_SEND_HIST_REQUEST_(_symbol, 1440)
        hist_db_key, trade_hist_df = self.send_hist_request(new_trade_dict)

        #Obtain Recent Account Information. Account Balance is most critical
        account_info = self.mt5_mvc.account_info()._asdict()

        symbol_info = self.mt5_mvc.symbols_get(new_trade_dict['symbol'])[0]._asdict()

        #Initiate  Risk Management Class
        # account balance
        # symbol
        self.trade_risk_calc = RiskManagement(mt5 = self.mt5_mvc,
                                        new_trade_dict= new_trade_dict,             # New Trade details
                                        risk_ratio= None,
                                        account_info= account_info,
                                        new_trade_df= trade_hist_df,
                                        hist_db_key= hist_db_key,
                                        symbol_info= symbol_info).calc_params()


        # self.new_trade_risk.calc_lot()
        return self.trade_risk_calc



    def send_hist_request(self,hist_request):
        """_summary_
        """
        if hist_request == {}:
            return print('Empty Request.')

        _symbol = hist_request.get('symbol', 'EURUSD')
        #A00 Change timestamp from daily.
        # MT5 Functionality, requires the timeframe to be stated as self.mt5_mvc.TIMEFRAME_M15
        _timeframe = '{}.{}'.format(MT5_OBJ_STRING,
                                        TIMEFRAMES_PERIODS[hist_request.get('timeframe', 1440)])

        #ADD able to add multiple requests???
        #create the label in the History_DB keys
        #A00 change timestamp. add try except loops
        hist_db_key = '{}_{}'.format(hist_request['symbol'],
                                    TIMEFRAMES_PERIODS[hist_request['timeframe']])
        _start = hist_request.get('start', None)
        _end = hist_request.get('end',Timestamp.now())

        #Get historical rates for the _symbol
        hist_rates = self.mt5_mvc.copy_rates_range(_symbol, eval(_timeframe), _start, _end)

        time.sleep(1)

        idx_n = 1
        while len(hist_rates) < 30:
            #Data duration statically selected to be set to be at least 30 data points from current time
            hist_request['start'] = (
                Timestamp.now() - Timedelta(minutes = (hist_request['timeframe'] * 48 * idx_n)))

            idx_n += 1
            _start = hist_request.get('start', None)

            #Get historical rates for the _symbol
            hist_rates = self.mt5_mvc.copy_rates_range(_symbol, eval(_timeframe), _start, _end)



        hist_db_df = DataFrame(hist_rates)

        hist_db_df['time'] = to_datetime(hist_db_df['time'], unit= 's')

        #Push collected data to data manipulation
        # to prepare DataFrames that may be utilised at any time
        #Create data manipulation object for basic Data Wrangling
        #Returns DataFrame with OHLC & atr
        hist_db_df = DataManipulation(hist_db_df).data_df

        return hist_db_key, hist_db_df


    def new_trade(self, new_trade, modif_trade):
        """_summary_

        Args:
            new_trade (_type_): _description_
            modif_trade (_type_): _description_
        """

        #MT5 API has different definitions for some of the dict parameters for a
        # new trade, which shall be changed

        symbol_info = self.mt5_mvc.symbol_info(new_trade['symbol'])._asdict()

        # time.sleep(0.5)

        trade_action = f"{MT5_OBJ_STRING}.{MT5_TRADE_ACTIONS['instant']}" \
                            if new_trade['price'] == 0 \
                            else f"{MT5_OBJ_STRING}.{MT5_TRADE_ACTIONS['pending']}"

        trade_type = f"{MT5_OBJ_STRING}.{MT5_ORDER_TYPES[new_trade['type']]}"

        if trade_action == 'self.mt5_mvc.TRADE_ACTION_DEAL':
            new_trade['price'] =  symbol_info['ask'] if trade_type == 'self.mt5_mvc.ORDER_TYPE_BUY' \
                        else symbol_info['bid'] if trade_type == 'self.mt5_mvc.ORDER_TYPE_SELL' \
                        else None

        else:
            new_trade['price'] = new_trade['price']

        #Modify Split Ratio based on tmeframe.
        if modif_trade['timeframe'] < 1440:         #Daily Timeframe
            modif_trade['split_ratio'] = 0.9
        else: modif_trade['split_ratio'] = 0.5
        
        

        new_trade['sl'] = new_trade['price'] - new_trade['SL_points'] \
            if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
                else new_trade['price'] + new_trade['SL_points']

        new_trade['tp'] = new_trade['price'] + new_trade['TP_points'] \
            if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
                else new_trade['price'] - new_trade['TP_points']
        # new_trade['sl'] = new_trade['price'] - new_trade['SL'] * symbol_info['point'] \
        #     if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
        #         else new_trade['price'] + new_trade['SL'] * symbol_info['point']

        # new_trade['tp'] = new_trade['price'] + new_trade['TP'] * symbol_info['point'] \
        #     if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
        #         else new_trade['price'] - new_trade['TP'] * symbol_info['point']

            
        #symbol_info['point'] holds the number of signficant decimal points for the financial instrument
        new_trade['scale_tp_by_3'] = new_trade['price'] + (3 * new_trade['TP_points']) \
            if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
                else new_trade['price'] - (3 * new_trade['TP_points'])

        new_trade['scale_tp_by_5'] = new_trade['price'] + (5 * new_trade['TP_points']) \
            if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
                else new_trade['price'] - (5 * new_trade['TP_points'])
        # new_trade['scale_tp_by_3'] = new_trade['price'] + (3 * new_trade['TP'] * symbol_info['point']) \
        #     if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
        #         else new_trade['price'] - (3 * new_trade['tp'] * symbol_info['point'])

        # new_trade['scale_tp_by_5'] = new_trade['price'] + (5 * new_trade['TP'] * symbol_info['point']) \
        #     if new_trade['type'] in ['BUY', 'BUY LIMIT', 'BUY STOP']\
        #         else new_trade['price'] - (5 * new_trade['tp'] * symbol_info['point'])

        type_filling = f"{MT5_OBJ_STRING}.{MT5_ORDER_TYPE_FILLING[symbol_info['filling_mode']]}"

        new_trade.update(
            {
                'action': eval(trade_action),

                # 'symbol': new_trade['_symbol'],

                # 'volume': new_trade['_lots'],

                'type': eval(trade_type),

                'deviation': 20,

                'type_filling': eval(type_filling),

                # 'comment': new_trade['_comment']

                # 'type_time': eval('{}.ORDER_TIME_GTC'.format(MT5_OBJ_STRING)),

                # 'expiration': symbol_info['expiration_time']

            }
        )
        # remove_keys= ['_action', '_type', '_symbol', '_price', '_SL',\
        #      '_TP', '_comment', '_magic', '_ticket','_lots']

        # [new_trade.pop(key, None) for key in remove_keys]

        #Declare multiple functions for the different trade strategies that could be implemented

        
        def minimal_trade():
            new_trade.update(
                {
                    'volume': ceil(new_trade['volume'] * 0.1 / symbol_info['volume_step']) \
                            * symbol_info['volume_step']     #Trade @ 10% of the Previous Risk Amount
                }
            )

            return (new_trade,)


        def single_trade():
            new_trade['volume'] = \
            ceil(new_trade['volume'] / symbol_info['volume_step']) \
            * symbol_info['volume_step']

            return (new_trade,)

        def two_way_split_trade():
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade
            new_trade_1['volume'] = \
                ceil(new_trade['volume'] * modif_trade['split_ratio'] / symbol_info['volume_step']) \
                * symbol_info['volume_step']
            #         new_trade['symbol'] in CURRENCY_METAL_PAIRS \
            #         else ceil((new_trade['volume'] * modif_trade['split_ratio'] *10))/10 if \
            #         new_trade['symbol'] in COMMODITIES_INDICES \
            #             else None

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2['volume'] = \
                ceil((new_trade['volume'] - new_trade_1['volume']) / symbol_info['volume_step']) \
                * symbol_info['volume_step']
                # if new_trade['symbol'] in CURRENCY_METAL_PAIRS \
                # else ceil((new_trade['volume'] - new_trade_1['volume']) *10)/10 \
                #     if new_trade['symbol'] in COMMODITIES_INDICES \
                #         else None

            new_trade_2.update(
                {
                'tp': new_trade['scale_tp_by_5']
                }
            )

            return (new_trade_1,new_trade_2)


        def three_way_split_trade():
            new_trade_1 = new_trade.copy()                      #Larger Proportional Trade (0.8)
            new_trade_1.update(
                {'volume': new_trade['volume'] * modif_trade['split_ratio'],}

            )

            new_trade_2 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_2.update(
                {
                    'volume': new_trade['volume'] \
                                * (1 - modif_trade['split_ratio']) \
                                * modif_trade['split_ratio_2'],
                    'tp': new_trade['scale_tp_by_3']
                }
            )

            new_trade_3 = new_trade.copy()                      #Smaller Proportional Trade
            new_trade_3.update(
                {
                    'volume': new_trade['volume'] - new_trade_1['volume'] - new_trade_2['volume'],
                    'tp': new_trade['scale_tp_by_5']
                }
            )

            return  (new_trade_1, new_trade_2, new_trade_3)


        trade_strategy_funcs = {
            'SINGLE TRADE': single_trade,
            '2-WAY SPLIT TRADE': two_way_split_trade,
            '3-WAY SPLIT TRADE': three_way_split_trade,
            'MINIMAL TRADE': minimal_trade
        }

        trades = trade_strategy_funcs.get\
            (modif_trade['trade_strategy'],'Failed to Capture Trade Strategy')()


        for trade in trades:

            result = self.mt5_mvc.order_send(trade)
            print(result.retcode)

            print(self.mt5_mvc.last_error())
            print(result._asdict().items())
            time.sleep(0.1)

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
                'AUS200',
                'CHINAH', 'HK50',
                'CN50',
                'JPN225',
                'EUSTX50', 'GER40', 'GERTEC30', 'NETH25', 'SCI25', 'SPA35', 'FRA40',
                'SWI20',
                'UK100',
                'US30', 'US500', 'US2000', 'USDX', 'NAS100', 'US100',
                'CA60',
                'SpotCrude', 'Cattle', 'Cotton', 'Copper', 'OrangeJuice',
                'Soybeans', 'SpotBrent'
                )

ALT_COMMODITIES_INDICIES= {
    'NAS100': ''
}

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
