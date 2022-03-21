"""[summary]

Returns:
    [type]: [description]
"""
import time
from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
import numpy as np
# import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class RiskManagement():
    """[summary]
    """
    def __init__(self, zmq_dwx = None,
                new_trade_dict = None,
                risk_ratio = None,
                account_info = None,
                new_trade_df = None,
                hist_db_key = None):

        self.new_trade_dict = new_trade_dict    #Dict containing the new trade's details

        if risk_ratio is None:
            risk_ratio = 0.02   # Default value for risk. 1% of the account.
        self.risk_ratio = risk_ratio

        self.risk_amount = None         #Determines stop loss placement

        if zmq_dwx is None:
            zmq_dwx = dwx()

        self.zmq_dwx = zmq_dwx          #zmq connection object

        self.new_trade_df = new_trade_df#DF containing historic data for ATR calculation

        self.account_info = account_info#Account information

        self.hist_db_key = hist_db_key#instrument key reference ie EURUSD_D1

        self._symbol = hist_db_key.partition('_')[0]    #Partitioning the symbol EURUSD_D1 to obtain instrument symbol

        self._timeframe = hist_db_key.partition('_')[2] #Partitioning the symbol EURUSD_D1 to obtain timeframe

        self.pip_value = None

        self.atr_in_pips = None

        self.stop_loss = None

        self.take_profit = None

        self.lot_size = None

        self.calc_pip_value = None

        self._symbol_bid = None

        self._symbol_ask = None

        self.sl_multiplier = 1.5

        self.tp_multiplier = 1


        self.sec_symbol = None

        #Major Currency pairs, where USD is the secondary currency traded.
        #ADD commodities ie XAG, XPT, XAU
        self.major_curr = ['AUD', 'EUR', 'GBP', 'NZD',  'XAG', 'XPT']

        # Exotic pairs whose values do not conform to typical 5 point values ie. SEK, JPY
        #ADD all necessary pairs to be considered
        self.exotic_curr = ['SEK', 'JPY', 'ZAR',]



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s
    def calc_lot(self):
        """[summary]
        """

        # Calculations for metal & FX pairs
        if self.new_trade_dict['instr_type'] == 'curr_mtl':
            try:
                
                #Get bid & ask prices of the _symbol
                self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)

                #check whether USD is part of the currency pair
                # ('USD' since this is the account currency)
                #A00 change so that the account currency is queried instead.
                if 'USD' in self._symbol:

                    #if USD is the first term in the currency pair ie. USDJPY, USDCAD
                    if 'USD' in self._symbol[:3]:
                        self.pip_value = 1 / ((self._symbol_bid + self._symbol_ask) / 2)

                    #ELSE USD is the second term in the currency pair, ie. NZDUSD, AUDUSD...
                    else:
                        self.pip_value = 1

                #if USD is not in the currency pair ie. AUDJPY, EURGBP...
                else:
                    #ADD Can be refracted to form a single function that calculates pip values

                    #Check whether _symbol contains one of the major pairs
                    # (where USD is the secondary currency.)
                    #If secondary symbol is a major currency ie. AUD, NZD, EUR, GBP...
                    if self._symbol[3:] in self.major_curr:
                        #sec_symbol of the trade combines the major pair & the USD for calculations
                        self.sec_symbol = self._symbol[3:] + 'USD'

                        # Collect bid/ask prices from Market_DB
                        sec_symbol_bid, sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                        self.pip_value = (sec_symbol_bid + sec_symbol_ask) / 2

                    #else secondary currency does not form a major pair with the USD
                    # ie. USDCAD, USDJPY...
                    else:
                        self.sec_symbol = 'USD' + self._symbol[3:]

                        # Collect bid/ask prices from Market_DB
                        sec_symbol_bid, sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                        self.pip_value = 1 / ((sec_symbol_bid + sec_symbol_ask) / 2)

                #ATR value from dataframe
                atr = self.new_trade_df['atr'].iloc[-1]

                # Calculate risk amount of the accountequity
                self.risk_amount = self.account_info['account_equity'] * self.risk_ratio


                # Calculate pip value for the trade
                # ie. Pip = %Risk Acct. Amount / Risk Stop Loss

                self.atr_in_pips = atr if self._symbol[:3] in \
                                ['XPT'] \
                            else atr * 10 if self._symbol[:3] in \
                                ['XAU', 'XPD'] \
                            else atr * 100 if self._symbol[:3] in \
                                ['XAG'] \
                                    or self._symbol[3:] in \
                                        ['JPY'] \
                            else atr * 1000 if self._symbol[:3] in \
                                ['SEK',] \
                            else atr * 10000 if self._symbol[:3] in \
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
                            else 0.1 * self.calc_pip_value / self.pip_value if \
                                self._symbol[:3] in \
                                ['XAU', 'XAG', 'XPD', 'XPT', \
                                'AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'NOK', 'NZD', 'SGD', 'USD'] \
                            else None

                # Calculate pip value for the trade
                # ie. Pip = %Risk Acct. Amount / Risk Stop Loss
                # if self._symbol[:3] not in self.exotic_curr and self._symbol[3:] not in self.exotic_curr:

                #     # self.atr_in_pips = self.calc_atr_pip_lot(pair_type = 'comm_pair')
                #     # self.atr_in_pips = atr * 10000

                #     # Calculate the Pip Value based on the new trade to be taken, ie.
                #     # Relating the risked amount (%Risk) to the risked pips
                #     # (stoplossMultiplier * ATR_in_pips)
                #     self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #     #To get the lot size, divide the current pip value of the
                #     # _symbol by the calculated pip value of the new trade
                #     # self.lot_size = self.calc_pip_value / self.pip_value
                #     # 0.1 refers to the lot size for a self.pip_value
                #     self.lot_size = 0.1 * self.calc_pip_value / self.pip_value

                # # Functionality for exotic pairs whose atr_in_pips may vary from the major pairs
                # #a00 functionality for indices
                # else:
                #     if self._symbol[3:] == 'JPY':
                #         self.atr_in_pips = atr * 100

                #         # Calculate the Pip Value based on the new trade to be taken, ie.
                #         # Relating the risked amount (%Risk) to the risked pips (factor * ATR_in_pips)
                #         self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #         #To get the lot size, divide the current pip value of the
                #         # _symbol by the calculated pip value of the new trade
                #         self.lot_size = 0.1 * self.calc_pip_value / self.pip_value * 0.01

                #     elif self._symbol[3:] == 'SEK' or self._symbol[3:] == 'ZAR':
                #         self.atr_in_pips = atr * 10000

                #         # Calculate the Pip Value based on the new trade to be taken, ie.
                #         # Relating the risked amount (%Risk) to the risked pips
                #         # (factor * ATR_in_pips)
                #         self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #         #To get the lot size, divide the current pip value of the _symbol
                #         # by the calculated pip value of the new trade
                #         self.lot_size = 0.1 * self.calc_pip_value / self.pip_value

                #         #Calculation for XAU
                #     elif self._symbol[:3] == 'XAU':

                #         self.atr_in_pips = self.calc_atr_pip_lot(pair_type = 'XAU')
                #         self.atr_in_pips = atr * 10

                #         # Calculate the Pip Value based on the new trade to be taken, ie.
                #         # Relating the risked amount (%Risk) to the risked pips
                #         # (factor * ATR_in_pips)
                #         self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #         #To get the lot size, divide the current pip value of the _symbol
                #         # by the calculated pip value of the new trade
                #         self.lot_size = 0.1 * self.calc_pip_value / self.pip_value


                self.stop_loss, self.take_profit = self.calc_sl_tp(atr)

            except Exception as ex:
                print(ex)

        # Calculations for Commodities & Indices
        else:
            try:
                # get bid ask prices
                self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)


                #calculate pip value of commodity or index
                # Pip values for indices is dependent on the country in question.
                #ie. GERTEC pip value would be determined based on the EURUSD price.
                #AUS200 would be determined based on the AUD USD qute price.
                #'USD' due to the current account type.


                    

                #For AUS200, query the AUDUSD price to calculate pip value
                if self._symbol in ['AUS200']:
                    audusd_bid, audusd_ask = self.bid_ask_price('AUDUSD')

                    #get pip value
                    self.pip_value = (audusd_bid + audusd_ask) / 2




                #For CHINAH, query the USDHKD price to calculate pip value
                if self._symbol in ['CHINAH']:
                    usdhkd_bid, usdhkd_ask = self.bid_ask_price('USDHKD')

                    #get pip value
                    self.pip_value = 1 / ((usdhkd_bid + usdhkd_ask) / 2)


                #For CN50, the pip value is taken as a 1:100 against the USD.
                #Similar scenario for US indices & commodities
                elif self._symbol in ['CN50', 'US30', 'US500', 'US2000', 'NAS100', 'USDX']:
                    self.pip_value = 1


                #For all EURO-ZONE indices, query the EURUSD price to calculate pip value
                elif self._symbol in ['GERTEC30', 'GER40', 'FRA40', 'SPA35', 'NETH25']:
                    eurusd_bid, eurusd_ask = self.bid_ask_price('EURUSD')

                    #get pip value
                    self.pip_value = (eurusd_bid + eurusd_ask) / 2


                #For UK100, query the GBPUSD price to calculate pip value
                elif self._symbol in ['UK100']:
                    gbpusd_bid, gbpusd_ask = self.bid_ask_price('GBPUSD')

                    #get pip value
                    self.pip_value = (gbpusd_bid + gbpusd_ask) / 2

                #For SCI25, query the USDSGD price to calculate pip value
                elif self._symbol in ['SCI25']:
                    usdsgd_bid, usdsgd_ask = self.bid_ask_price('USDSGD')

                    #get pip value
                    self.pip_value = 1 / ((usdsgd_bid + usdsgd_ask) / 2)


                elif self._symbol in ['SpotBrent']:
                    self.pip_value = 1


                # account currency consideration

                # calculate atr
                atr = self.new_trade_df['atr'].iloc[-1]

                # calculate risk amount
                self.risk_amount = self.account_info['account_balance'] * self.risk_ratio

                # calculate atr in pips
                self.atr_in_pips = atr if self._symbol in \
                                        ['AUS200', 'CHINAH', 'CN50','FRA40', \
                                        'HK50', 'JPN225', 'GER40', 'NAS100', \
                                        'SCI25', 'SPA35', 'UK100', 'US30', \
                                        'US500', 'US2000','Soybeans'] \
                                    else atr * 10 if self._symbol in \
                                        [ 'GERTEC30', 'NETH25'] \
                                    else atr * 100 if self._symbol in \
                                        ['USDX', 'SpotCrude', 'Cotton', 'SpotBrent'] \
                                    else atr * 1000 if self._symbol in \
                                        ['Copper'] \
                                    else atr * 10000 if self._symbol in \
                                        ['Cattle'] \
                                    else None

                # calculate the pip value based on the trade to be taken
                self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #For testing purposes, Risk amount == 500
                # self.calc_pip_value = 50 / (self.atr_in_pips * self.sl_multiplier)

                # calculate lot size
                self.lot_size = self.calc_pip_value / self.pip_value

                # Calculate SL & TP
                self.stop_loss, self.take_profit = self.calc_sl_tp(atr)
                
            except Exception as ex:
                print(ex)


    # calculate Stop Loss
    #A00 add functionality depending on whether trade is sell or buy, ie using buy or sell value?
    def calc_sl_tp(self, atr):
        """[summary]

        Args:
            atr ([type]): [description]

        Returns:
            [type]: [description]
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
            sl_pips = self.new_trade_dict['buy_sell_limit'] - self.sl_multiplier * atr
            tp_pips = self.new_trade_dict['buy_sell_limit'] + self.tp_multiplier * atr   
            
            return sl_pips, tp_pips

        def sell_limit_order():
            sl_pips = self.new_trade_dict['buy_sell_limit'] + self.sl_multiplier * atr
            tp_pips = self.new_trade_dict['buy_sell_limit'] - self.tp_multiplier * atr
            
            return sl_pips, tp_pips

        order_type = {
            'BUY': buy_order,
            'SELL': sell_order,
            'BUY LIMIT': buy_limit_order,
            'SELL LIMIT': sell_limit_order
        }
        sl_pips, tp_pips = order_type.get(self.new_trade_dict['_order'])()


        return sl_pips, tp_pips


    # Collect bid & ask prices of specific symbol after downloading current rates
    def bid_ask_price(self, _symbol):
        """[summary]

        Args:
            _symbol (INSTRUMENT): [Instrument to request bid/ask]

        Returns:
            [bid & ask price]: [Instant bid as prices for the instrument]
        """

        #USING SUBSCRIPTION REQUESTS
        # self.zmq_dwx._DWX_MTX_SUBSCRIBE_MARKETDATA_(_symbol)
        # time.sleep(1)

        # self.zmq_dwx._DWX_MTX_SEND_TRACKPRICES_REQUEST_([_symbol])

        # #Pause to allow Market DB to be updated with recent values
        # time.sleep(1)

        # # Get last item in the dict for the symbol
        # _symbol_bid, _symbol_ask = list(self.zmq_dwx._Market_Data_DB[_symbol].values())[-1]

        # self.zmq_dwx._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()
        # self.zmq_dwx._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()

        #USING INSTANT RATES REQUESTS
        self.zmq_dwx._DWX_MTX_GET_INSTANT_RATES_(_symbol)
        time.sleep(0.05)

        _symbol_bid, _symbol_ask = [self.zmq_dwx.instant_rates_DB[_symbol][-1].get(key) for key in ['_bid', '_ask']]

        return _symbol_bid, _symbol_ask

    # Create process that monitors specific trade scenarios.
