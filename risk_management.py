"""[summary]

Returns:
    [type]: [description]
"""
import time
# from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
import numpy as np
# import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class RiskManagement():
    """[summary]
    """
    def __init__(self, dwx,
                new_trade_dict = None,
                risk_ratio = None,
                account_info = None,
                new_trade_df = None,
                hist_db_key = None):

        self.trade_dict = new_trade_dict    #Dict containing the new trade's details

        if risk_ratio is None:
            risk_ratio = 0.02   # Default value for risk. >1% of the account.
        self.risk_ratio = risk_ratio

        self.risk_amount = None         #Determines stop loss placement

        self.dwx = dwx          #dwx connection object. Either DWXClient, or DWXConn

        self.trade_df = new_trade_df#DF containing historic data for ATR calculation

        self.account_info = account_info#Account information

        self.hist_db_key = hist_db_key#instrument key reference ie EURUSD_D1

        self._symbol = hist_db_key.partition('_')[0]    #Partitioning the symbol EURUSD_D1 to obtain instrument symbol

        self._timeframe = hist_db_key.partition('_')[2] #Partitioning the symbol EURUSD_D1 to obtain timeframe

        self._symbol_info = self.dwx.symbol_info(self._symbol)._asdict() if hasattr(self.dwx, 'symbol_info') \
                                else None

        self._symbol_bid = None

        self._symbol_ask = None

        self.sec_symbol = None

        self.sec_symbol_bid = None

        self.sec_symbol_ask = None

        self.atr = None
        
        self.pip_value = None

        self.calc_pip_value = None

        self.atr_in_pips = None

        self.lot_size = None

        self.sl_multiplier = 1.5

        self.tp_multiplier = 1

        self.stop_loss = None

        self.take_profit = None

        



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s
    def calc_lot(self):
        """[summary]
        """

        # Calculations for metals & FX pairs
        if self.trade_dict['instr_type'] == 'curr_mtl':
            try:
                
                #Get bid & ask prices of the _symbol
                self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)

                #check whether USD is part of the currency pair
                # ('USD' since this is the account currency)
                #A00 change so that the account currency is queried instead.
                if 'USD' in self._symbol:

                    #IF USD is the second term in the currency pair, ie. NZDUSD, AUDUSD
                    # Pip value is equal to 1
                    #elif USD is the first term in the currency pair ie. USDJPY, USDCAD
                    # Pip value is given by the inverse of the market price
                    #We take the avg of bid & ask, & get the inverse
                    self.pip_value = 1 if 'USD' in self._symbol[3:] \
                            else 1 / ((self._symbol_bid + self._symbol_ask) / 2)


                #if USD is not in the currency pair ie. AUDJPY, EURGBP...
                else:
                    #ADD Can be refracted to form a single function that calculates pip values


                    #Check whether the secondary currency in _symbol contains one of the currencies
                    # where USD is the secondary currency in its USD pair ie. AUDUSD, GBPUSD...
                    #If secondary symbol is a major currency ie. AUD, NZD, EUR, GBP...
                    #else secondary currency  IN _symbol does not form a pair with the USD
                    # as the secondary currency ie. USDCAD, USDJPY...
                    # ie. for the EURGBP pair, the sec_symbol shall be GBPUSD (if)
                    # ie. for the AUDJPY pair, the sec_symbol shall be USDJPY (else)
                    self.sec_symbol = self._symbol[3:] + 'USD' if self._symbol[3:] \
                            in MAJOR_CURRENCY else 'USD' + self._symbol[3:]

                    # Collect bid/ask prices for the secondary symbol from Market_DB
                    self.sec_symbol_bid, self.sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                    #if USD is the first term in the currency pair ie. USDJPY, USDCAD
                    # Pip value is given by the inverse of the market price
                    #We take the avg of bid & ask, & get the inverse
                    #ELSE USD is the second term in the currency pair, ie. NZDUSD, AUDUSD
                    # Pip value is equal to 1
                    self.pip_value = (self.sec_symbol_bid + self.sec_symbol_ask) / 2 if 'USD' in self.sec_symbol[3:] \
                            else 1 / ((self.sec_symbol_bid + self.sec_symbol_ask) / 2)


                #ATR value from dataframe
                self.atr = self.trade_df['atr'].iloc[-1]

                # Calculate risk amount of the account balance
                self.risk_amount = self.account_info['balance'] * self.risk_ratio
                


                # Calculate ATR in pip value for the pair
                # Variations are dependent on how the ATR is calculated for
                # the _symbol
                self.atr_in_pips = self.atr * 10 if self._symbol[:3] in \
                                ['XAU','XPD','XPT'] \
                            else self.atr * 100 if self._symbol[:3] in \
                                ['XAG'] \
                                    or self._symbol[3:] in \
                                        ['JPY'] \
                            else self.atr * 1000 if self._symbol[:3] in \
                                ['SEK',] \
                            else self.atr * 10000 if self._symbol[:3] in \
                                ['AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'NOK', 'NZD', 'SGD', 'USD'] \
                            else None

                # Calculate the Pip Value based on the new trade to be taken, ie.
                # Relating the risked amount (%Risk) to the risked pips
                # (stoplossMultiplier * ATR_in_pips)
                self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)


                #To get the lot size, divide the current pip value of the
                # _symbol by the calculated pip value of the new trade
                # self.lot_size = self.calc_pip_value / self.pip_value
                # 0.1 refers to the lot size for a self.pip_value
                self.lot_size = 0.1 * self.calc_pip_value / self.pip_value * 0.01 if \
                                self._symbol[3:] in ['JPY'] \
                            else 0.1 * self.calc_pip_value/ self.pip_value * 100 if \
                                self._symbol[:3] in ['XAU'] \
                            else 0.1 * self.calc_pip_value / self.pip_value if \
                                self._symbol[:3] in \
                                ['XAU', 'XAG', 'XPD', 'XPT', \
                                'AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'NOK', 'NZD', 'SGD', 'USD'] \
                            else None


                self.stop_loss, self.take_profit = self.calc_sl_tp(self.atr)

            except Exception as ex:
                ex_str = 'Exception Type: {0}. Args:\n{1!r}'
                ex_msg = ex_str.format(type(ex).__name__, ex.args)
                print(ex_msg)





        # Calculations for Commodities & Indices
        else:
            try:
                # get bid ask prices
                self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)


                #calculate pip value of commodity or index
                # Pip values for indices is dependent on the _symbol's jurisdiction.
                #ie. GERTEC pip value would be determined based on the EURUSD price.
                #AUS200 would be determined based on the AUDUSD quote price.
                #'USD' due to the current account type.

                # IF in the following list, the pip_value is directly pegged to the USD value.
                # ie. the _symbol for US30 would be US30USD
                if self._symbol in USD_BASED_INDICES_COMMODITIES:
                    self.pip_value = 1
                
                # ELSE remaining list of indices & commodities are based on
                #different currency pairs, as populated in the
                #INDICES_SECONDARY_SYMBOL dictionary
                else:
                    
                    self.sec_symbol = INDICES_SECONDARY_SYMBOL.get(self._symbol)
                    
                    self.sec_symbol_bid, self.sec_symbol_ask = \
                        self.bid_ask_price(self.sec_symbol)

                    self.pip_value = (self.sec_symbol_bid + self.sec_symbol_ask) / 2 if 'USD' in self.sec_symbol[3:] \
                        else 1 / ((self.sec_symbol_bid + self.sec_symbol_ask) / 2)


                # obtin atr from DF
                self.atr = self.trade_df['atr'].iloc[-1]
                
                self.atr += self._symbol_info['spread'] * self._symbol_info['point']

                # calculate risk amount
                self.risk_amount = self.account_info['balance'] * self.risk_ratio
                
                #For testing at different account sizes
                # self.risk_amount = 100000 * self.risk_ratio

                # calculate atr in pips
                self.atr_in_pips = self.atr if self._symbol in \
                                        ['AUS200', 'CHINAH', 'CN50','FRA40', \
                                        'HK50', 'JPN225', 'GER40', 'NAS100', \
                                        'SCI25', 'SPA35', 'UK100', 'US30', \
                                        'US500', 'US2000','Soybeans'] \
                                    else self.atr * 10 if self._symbol in \
                                        [ 'GERTEC30', 'NETH25'] \
                                    else self.atr * 100 if self._symbol in \
                                        ['USDX', 'SpotCrude', 'Cotton', 'SpotBrent'] \
                                    else self.atr * 1000 if self._symbol in \
                                        ['Copper'] \
                                    else self.atr * 10000 if self._symbol in \
                                        ['Cattle'] \
                                    else None

                # calculate the pip value based on the trade to be taken
                self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #For testing purposes, Risk amount == 500
                # self.calc_pip_value = 500 / (self.atr_in_pips * self.sl_multiplier)

                # calculate lot size
                self.lot_size = np.round(self.calc_pip_value / self.pip_value, 1) * 10 if \
                                    self._symbol in ['NETH25'] else \
                                    np.round(self.calc_pip_value / self.pip_value,1) * 0.01 if \
                                        self._symbol in ['JPN225'] \
                                    else np.round(self.calc_pip_value / self.pip_value, 1)


                # Calculate SL & TP
                self.stop_loss, self.take_profit = self.calc_sl_tp(self.atr)
                pass
                
            except Exception as ex:
                ex_str = 'Exception Type: {0} Args: \n {1!r}'
                ex_msg = ex_str.format(type(ex).__name__,ex.args)
                print(ex_msg)


    # calculate Stop Loss
    #A00 add functionality depending on whether trade is sell or buy, ie using buy or sell value?
    def calc_sl_tp(self, atr):
        """[summary]

        Args:
            atr ([float]): [ATR range from trade_df]

        Returns:
            [float]: [SL level ]
            [float]: [TP Level]
        """

        def buy_order():
            sl_pips = self._symbol_ask - self.sl_multiplier * atr
            tp_pips = self._symbol_ask + self.tp_multiplier * atr

            return sl_pips, tp_pips

        def sell_order():
            sl_pips = self._symbol_bid + self.sl_multiplier * atr
            tp_pips = self._symbol_bid - self.tp_multiplier * atr

            return sl_pips, tp_pips

        def buy_limit_order():
            sl_pips = self.trade_dict['buy_sell_limit'] - self.sl_multiplier * atr
            tp_pips = self.trade_dict['buy_sell_limit'] + self.tp_multiplier * atr
            
            return sl_pips, tp_pips

        def sell_limit_order():
            sl_pips = self.trade_dict['buy_sell_limit'] + self.sl_multiplier * atr
            tp_pips = self.trade_dict['buy_sell_limit'] - self.tp_multiplier * atr
            
            return sl_pips, tp_pips

        order_type = {
            'BUY': buy_order,
            'SELL': sell_order,
            'BUY LIMIT': buy_limit_order,
            'SELL LIMIT': sell_limit_order
        }
        sl_pips, tp_pips = order_type.get(self.trade_dict['_order'])()


        return sl_pips, tp_pips


    # Collect bid & ask prices of specific symbol after downloading current rates
    def bid_ask_price(self, _symbol):
        """[summary]

        Args:
            _symbol (INSTRUMENT): [Instrument to request bid/ask]

        Returns:
            [bid & ask price]: [Instant bid as prices for the instrument]
        """
        # confirm if Connection API  in use depending on attribute availability
        # OPTIONS ARE: MT5 API, DWXConn Client, DWXZMQ connection

        # Priority to MT5 API
        if hasattr(self.dwx, 'TIMEFRAME_D1'):
            _symbol_tick_dict = self.dwx.symbol_info_tick(_symbol)._asdict()

            return _symbol_tick_dict['bid'], _symbol_tick_dict['ask'] 


        elif hasattr(self.dwx, 'subscribe_symbols'):

            #Get bid & ask prices of the _symbol
            self.dwx.subscribe_symbols([_symbol])

            time.sleep(0.5)

            _symbol_bid, _symbol_ask = [self.dwx.market_data[_symbol].get(key) for key in ['bid', 'ask']]

            return _symbol_bid, _symbol_ask

        else:
            #utilize the DWX_ZMQ Class for the market data
            #Get bid & ask prices of the _symbol
            self.dwx._DWX_MTX_GET_INSTANT_RATES_(_symbol)
            time.sleep(0.5)

            _symbol_bid, _symbol_ask = [self.dwx.instant_rates_DB[_symbol][-1].get(key) for key in ['_bid', '_ask']]

            return _symbol_bid, _symbol_ask

    # Create process that monitors specific trade scenarios.



###############################################

# DECLARATION OF GLOBAL VARIABLES FOR THE CLASS ABOVE

###############################################


# #Major Currency pairs, where USD is the secondary currency traded.
# #ADD commodities ie XAG, XPT, XAU
MAJOR_CURRENCY = ('AUD', 'EUR', 'GBP', 'NZD', 'XAU', 'XAG', 'XPT', 'XPD')

# # Exotic pairs whose values do not conform to typical 5 point values ie. SEK, JPY
# #ADD all necessary pairs to be considered
EXOTIC_CURRENCY = ('SEK', 'JPY', 'ZAR',)

USD_BASED_INDICES_COMMODITIES =  (
                'CN50', 'US30', 'US500', 'US2000', 'NAS100', 'USDX', 'SpotBrent'
)

INDICES_SECONDARY_SYMBOL = {
                'AUS200': 'AUDUSD',
                'CHINAH': 'USDHKD',
                'JP225': 'USDJPY',
                'HK50': 'USDHKD',
                'GERTEC30': 'EURUSD', 'GER40': 'EURUSD',
                'FRA40': 'EURUSD', 'SPA35': 'EURUSD',
                'NETH25': 'EURUSD', 'EUSTX50':'EURUSD',
                'UK100': 'GBPUSD',
                'SCI25': 'USDSGD',
                'JPN225':'USDJPY',
                'SWI20':'USDCHF',
                'CA60': 'USDCAD'
                            }
