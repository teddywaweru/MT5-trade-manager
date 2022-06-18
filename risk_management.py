"""[summary]

Returns:
    [type]: [description]
"""

# pylint: disable=broad-except


# import time
# from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
# import numpy as np
import traceback
# import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class RiskManagement():
    """[summary]
    """
    def __init__(self,
                mt5= None,
                new_trade_dict = None,
                risk = None,
                account_info = None,
                new_trade_df = None,
                symbol_info= None):

        self.trade_dict = new_trade_dict    #Dict containing the new trade's details

        if risk is None:
            risk = 0.02   # Default value for risk. >1% of the account.
        self.risk = risk

        self.risk_amount = None         #Determines stop loss placement

        self.mt5 = mt5

        self.trade_df = new_trade_df#DF containing historic data for ATR calculation

        self.account_info = account_info#Account information

        self.symbol_info = symbol_info

        if self.symbol_info['digits'] == 1:
            self.symbol_info['point'] = 0.3      #Static declarations for singular points scenarios

        self.symbol = self.symbol_info['name']

        self.symbol_bid = None

        self.symbol_ask = None

        self.sec_symbol = None

        self.sec_symbol_bid = None

        self.sec_symbol_ask = None

        self.atr = None

        self.symbol_value = None

        self.calc_pip_value = None

        self.atr_in_points = None

        self.lot_size = None

       
       #Statically declare SL_Multiplier.
    #    1.5 for daily timeframe orders, $ for lower timeframes
       #ADD user input.
        self.sl_multiplier = 3  if self.trade_dict['timeframe'] < 1440 \
                                    else 1.5

        self.tp_multiplier = 1

        self.stop_loss = None

        self.take_profit = None



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s
    def calc_params(self):
        """[summary]
        """

        # Calculations for metals & FX pairs
        try:

            #Get bid & ask prices of the symbol
            self.symbol_bid, self.symbol_ask = self.bid_ask_price(self.symbol)

            #check whether the account currency is part of the symbol
            #Specifically implemented for FX pairs, but will automatically
            # cancel out other symbols ie. INDICES, COMMODITIES
            #Special inference on currency indices ie USDX,
            # but current tests show that these are also calculable with the below method.
            if self.account_info['currency'] in self.symbol:

                #IF account currency is the second term in the currency pair,
                # ie. NZDUSD, AUDUSD for USD based account
                # Pip value is equal to 1
                #elif account currency is the first term in the currency pair
                # ie. USDJPY, USDCAD, USDX
                # Pip value is given by the inverse of the market price
                #We take the avg of bid & ask, & get the inverse
                self.symbol_value = 1 if self.account_info['currency'] in self.symbol[3:] \
                        else 1 / ((self.symbol_bid + self.symbol_ask) / 2)

                #ntended for XAG & JPY calculations.
                if self.symbol_info['digits'] == 3 and 'JPY' in self.symbol:
                    self.symbol_value = self.symbol_value / 0.01



            #else if account currency is not in the symbol
            # ie. AUDJPY, EURGBP for a USD based account currency
            else:

                #If the account currency matches the currency_profit
                #ie. US500 for USD based account,  or GER40 for EUR based account.
                if self.symbol_info['currency_profit'] == self.account_info['currency']:
                    self.symbol_value = 1


                #else Create the sec_symbol using the
                # account currency & the symbol's currency_profit
                # ie. 'USD' + 'EUR' for GER40Cash, 'USD' + 'CAD' for AUDCAD,
                # 'USD' + 'AUD' for AUS200; for USD based account
                else:
                    self.sec_symbol = self.account_info['currency'] + \
                                        self.symbol_info['currency_profit']

                    #Confirm if sec_symbol is a valid combo.
                    if self.mt5.symbols_get(self.sec_symbol):
                        pass

                    #Else, flip the currency order
                    #A00 include instances when symbol is completely invalid in both circumstances
                    #A00 develop & test out above scenarios
                    else:

                        self.sec_symbol = self.symbol_info['currency_profit'] + \
                                            self.account_info['currency']


                    # Collect bid/ask prices for the secondary symbol
                    self.sec_symbol_bid, self.sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                    #if account currency is the first term
                    # in the currency pair ie. USDJPY, USDCAD in USD based account
                    # Symbol value is given by the inverse of the market price
                    #We take the avg of bid & ask, & get the inverse
                    #ELSE if account currency is the second term
                    # in the currency pair, ie. NZDUSD, AUDUSD
                    # Symbol value is equal to 1
                    self.symbol_value = (self.sec_symbol_bid + self.sec_symbol_ask) / 2 \
                                        if self.account_info['currency'] in self.sec_symbol[3:] \
                                        else 1 / ((self.sec_symbol_bid + self.sec_symbol_ask) / 2)

                    #ntended for XAG & JPY calculations.
                    if 'JPY' in self.sec_symbol:
                        self.symbol_value = self.symbol_value / 0.01



            #ATR value from dataframe
            self.atr = self.trade_df['atr'].iloc[-1]

            #Include spread value into atr
            #AFF may be included
            # self.atr = self.atr + self.symbol_info['spread'] * self.symbol_info['point']


            # Calculate risk amount of the account balance
            self.risk_amount = self.account_info['balance'] * self.risk

            #Convert ATR to Points

            self.atr_in_points = self.atr / self.symbol_info['point']



            # Calculate the Pip Value based on the new trade to be taken, ie.
            # Relating the risked amount (%Risk) to the risked pips
            # (stoplossMultiplier * ATR_in_pips)
            self.calc_pip_value = self.risk_amount / (self.atr_in_points * self.sl_multiplier)


            #To get the lot size, divide the current pip value of the
            # symbol by the calculated pip value of the new trade
            # https://www.myfxbook.com/forex-calculators/pip-calculator#:~:text=How%20to%20calculate%20the%20value%20of%20a%20pip%3F
            self.lot_size = self.calc_pip_value / self.symbol_value


            # The TRADE_CALC_MODE enumeration is used for obtaining information
            # about how the margin requirements for a symbol are calculated.
            # FOR CFDs & Crypto, the leverage is not included in the margin calculation

            # https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants
            if self.symbol_info['trade_calc_mode'] in [0]:
                self.lot_size = self.lot_size * self.symbol_info['point'] \
                                * 10**self.symbol_info['digits']

                # For XAG, contract size is taken as 5000 typicaly, & this is required to
                # be standardized for the lot size to be valid.
                if 'XAG' in self.symbol:
                    self.lot_size = self.lot_size / \
                        (self.symbol_info['trade_contract_size'] * self.symbol_info['point'])
                # self.lot_size = self.lot_size * self.symbol_info['point'] \
                #                 * self.symbol_info['trade_contract_size']


            elif self.symbol_info['trade_calc_mode'] in [2,4]:
                self.lot_size = self.lot_size /  self.symbol_info['point']


            self.stop_loss, self.take_profit = self.calc_sl_tp(atr= self.atr)

            return self

        except Exception:
            traceback.print_exc()


    # calculate Stop Loss & Take Profit
    def calc_sl_tp(self, atr):
        """[summary]

        Args:
            atr ([float]): [ATR range from trade_df]

        Returns:
            [float]: [SL level ]
            [float]: [TP Level]
        """

        def buy_order():
            sl_pips = self.symbol_bid - self.sl_multiplier * atr
            tp_pips = self.symbol_ask + self.tp_multiplier * atr

            return sl_pips, tp_pips

        def sell_order():
            sl_pips = self.symbol_ask + self.sl_multiplier * atr
            tp_pips = self.symbol_bid - self.tp_multiplier * atr

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
        sl_pips, tp_pips = order_type.get(self.trade_dict['order'])()


        return sl_pips, tp_pips


    # Collect bid & ask prices of specific symbol after downloading current rates
    def bid_ask_price(self, symbol):
        """[summary]

        Args:
            symbol (INSTRUMENT): [Instrument to request bid/ask]

        Returns:
            [bid & ask price]: [Instant bid as prices for the instrument]
        """
        # confirm if Connection API  in use depending on attribute availability
        # OPTIONS ARE: MT5 API, DWXConn Client, DWXZMQ connection

        # Priority to MT5 API
        # if hasattr(self.mt5, 'TIMEFRAME_D1'):
        symbol_tick_dict = self.mt5.symbol_info_tick(symbol)._asdict()

        return symbol_tick_dict['bid'], symbol_tick_dict['ask']












        #-----------------------------23/05/2022----------------------------

        #Code segment for requesting bid ask prices from DWX APIs. Discontinued on above date.

        # elif hasattr(self.mt5, 'subscribe_symbols'):

        #     #Get bid & ask prices of the symbol
        #     self.mt5.subscribe_symbols([symbol])

        #     time.sleep(0.5)

        #     _symbol_bid, _symbol_ask = [self.mt5.market_data[symbol].get(key) \
                                        # for key in ['bid', 'ask']]

        #     return _symbol_bid, _symbol_ask

        # else:
        #     #utilize the DWX_ZMQ Class for the market data
        #     #Get bid & ask prices of the symbol
        #     self.mt5._DWX_MTX_GET_INSTANT_RATES_(symbol)
        #     time.sleep(0.5)

        #     _symbol_bid, _symbol_ask = [self.mt5.instant_rates_DB[symbol][-1].get(key) \
                                        # for key in ['_bid', '_ask']]

        #     return _symbol_bid, _symbol_ask

    # Create process that monitors specific trade scenarios.



###############################################

# DECLARATION OF GLOBAL VARIABLES FOR THE CLASS ABOVE

###############################################


# # #Major Currency pairs, where USD is the secondary currency traded.
# # #ADD commodities ie XAG, XPT, XAU
# MAJOR_CURRENCY = ('AUD', 'EUR', 'GBP', 'NZD', 'XAU', 'XAG', 'XPT', 'XPD')

# # # Exotic pairs whose values do not conform to typical 5 point values ie. SEK, JPY
# # #ADD all necessary pairs to be considered
# EXOTIC_CURRENCY = ('SEK', 'JPY', 'ZAR',)

# USD_BASED_INDICES_COMMODITIES =  (
#                 'CN50', 'US30', 'US500', 'US2000', 'NAS100', 'USDX', 'SpotBrent'
# )

# INDICES_SECONDARY_SYMBOL = {
#                 'AUS200': 'AUDUSD',
#                 'CHINAH': 'USDHKD',
#                 'JP225': 'USDJPY',
#                 'HK50': 'USDHKD',
#                 'GERTEC30': 'EURUSD', 'GER40': 'EURUSD',
#                 'FRA40': 'EURUSD', 'SPA35': 'EURUSD',
#                 'NETH25': 'EURUSD', 'EUSTX50':'EURUSD',
#                 'UK100': 'GBPUSD',
#                 'SCI25': 'USDSGD',
#                 'JPN225':'USDJPY',
#                 'SWI20':'USDCHF',
#                 'CA60': 'USDCAD'
#                             }
