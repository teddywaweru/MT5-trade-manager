"""[summary]

Returns:
    [type]: [description]
"""
import time
from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
# import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class RiskManagement():
    """[summary]
    """
    def __init__(self, zmq_dwx = None,
                _order = 'SELL',
                risk_ratio = None,
                account_info = None,
                new_trade_df = None,
                hist_db_key = None):

        if risk_ratio is None:
            risk_ratio = 0.02   # Default value for risk. 1% of the account.
        self.risk_ratio = risk_ratio
        self.risk_amount = None
        if zmq_dwx is None:
            zmq_dwx = dwx()
        self.zmq_dwx = zmq_dwx
        self.new_trade_df = new_trade_df
        self.account_info = account_info
        self.hist_db_key = hist_db_key
        self._symbol = hist_db_key[:6]
        self._timeframe = hist_db_key[7:]

        self.pip_value = None

        self._order = _order

        self.atr_in_pips = None

        self.stop_loss = None

        self.take_profit = None

        self.lot_size = None

        self.calc_pip_value = None

        self._symbol_bid = None

        self._symbol_ask = None

        self.sl_multiplier = 1.5

        self.tp_multiplier = 2


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

        try:
            
            #Allow time for the values to be loaded onto the Market_DB dict.

            self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)

            #check whether USD is part of the currency pair
            # ('USD' since this is the account currency)
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

            self.atr_in_pips = atr * 10 if self._symbol[:3] in \
                                ['XAU', 'XPD', 'XPT'] \
                        else atr * 100 if self._symbol[:3] in \
                            ['XAG'] \
                                or self._symbol[3:] in \
                                    ['JPY'] \
                        else atr * 1000 if self._symbol[:3] in \
                            ['SEK',] \
                        else atr * 10000 if self._symbol[:3] in \
                            ['AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'NZD', 'SGD', 'USD'] \
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
                            'AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'NZD', 'SGD', 'USD'] \
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


            self.stop_loss = self.calc_stop_loss(atr)
            self.take_profit = self.calc_take_profit(atr)

        except Exception as ex:
            print(ex)


    # calculate Stop Loss
    #A00 add functionality depending on whether trade is sell or buy, ie using buy or sell value?
    def calc_stop_loss(self, atr):
        """[summary]

        Args:
            atr ([type]): [description]

        Returns:
            [type]: [description]
        """
        # SL calculated as 1.5x of ATR
        if self._order == 'BUY':
            stop_loss_pips = self._symbol_ask - self.sl_multiplier * atr

        else:
            stop_loss_pips = self._symbol_bid + self.sl_multiplier * atr

        return stop_loss_pips

    # Calculate Take Profit
    def calc_take_profit(self, atr):
        """[summary]

        Args:
            atr ([type]): [description]

        Returns:
            [type]: [description]
        """

        if self._order == 'BUY':
            take_profit_pips = self._symbol_ask + self.tp_multiplier * atr

        else:
            take_profit_pips = self._symbol_bid - self.tp_multiplier * atr

        return take_profit_pips
        # TP calculated as 1.5x of ATR


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
