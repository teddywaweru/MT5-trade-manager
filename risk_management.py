from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
import time
import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class risk_management():

    
    def __init__(self, ZMQ_ = None,
                _order = 'SELL',
                risk_ratio = None,
                account_info = None,
                new_trade_df = None,
                hist_db_key = None):
        
        if risk_ratio is None:
            risk_ratio = 0.005     # Default value for risk. 0.5% of the account.
        self.risk_ratio = risk_ratio
        self.risk_amount = None
        if ZMQ_ is None:
            ZMQ_ = dwx()
        self.ZMQ_ = ZMQ_
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

        self.tp_multiplier = 1
        
        
        
        self.sec_symbol = None

        #Major Currency pairs, where USD is the secondary currency traded.
        #ADD commodities ie XAG, XPT, XAU
        self.major_curr = ['AUD', 'EUR', 'GBP', 'NZD', 'XAU', 'XAG', 'XPT']

        # Exotic pairs whose values do not conform to typical 5 point values ie. SEK, JPY
        #ADD all necessary pairs to be considered
        self.exotic_curr = ['SEK', 'JPY', 'ZAR',]



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s
    def calc_lot(self):

        try:
            #Subscribe to market data of _symbol
            self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(self._symbol)
            time.sleep(1)

            #Request for Current Tracked Prices.
            self.ZMQ_._DWX_MTX_SEND_TRACKPRICES_REQUEST_([self._symbol])
            time.sleep(1)

            #Allow time for the values to be loaded onto the Market_DB dict.

            self._symbol_bid, self._symbol_ask = self.bid_ask_price(self._symbol)

            #check whether USD is part of the currency pair ('USD' since this is the account currency)
            if 'USD' in self._symbol:
                
                if 'USD' in self._symbol[:3]:
                    self.pip_value = 1 / ((self._symbol_bid + self._symbol_ask) / 2)

                else:
                    self.pip_value = 1
            
            else:

                #Check whether _symbol contains one of the major pairs (where USD is the secondary currency.)
                #If first part of the symbol is a major currency pair ie. AUD, NZD, EUR, GBP...
                if self._symbol[3:] in self.major_curr:
                    
                    self.sec_symbol = self._symbol[3:] + 'USD'

                    # Collect bid/ask prices from Market_DB
                    sec_symbol_bid, sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                    self.pip_value = (sec_symbol_bid + sec_symbol_ask) / 2

                    self.ZMQ_._DWX_MTX_UNSUBSCRIBE_MARKETDATA_(self.sec_symbol)
                    #Unsubscribe from marketdata

                else:
                    self.sec_symbol = 'USD' + self._symbol[3:]

                    # Collect bid/ask prices from Market_DB
                    sec_symbol_bid, sec_symbol_ask = self.bid_ask_price(self.sec_symbol)

                    self.pip_value = 1 / ((sec_symbol_bid + sec_symbol_ask) / 2)

            #ATR value from dataframe
            atr = self.new_trade_df['atr'].iloc[-1]

            # Calculate risk amount of the accountbalance
            self.risk_amount = self.account_info['account_equity'] * self.risk_ratio
            print(self.risk_amount)


            # Calculate pip value for the trade ie. Pip = %Risk Acct. Amount / Risk Stop Loss
            if self._symbol[:3] not in self.exotic_curr and self._symbol[3:] not in self.exotic_curr:

                self.atr_in_pips = atr * 10000

                # Calculate the Pip Value based on the new trade to be taken, ie.
                # Relating the risked amount (%Risk) to the risked pips (stoplossMultiplier * ATR_in_pips) 
                self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                #To get the lot size, divide the current pip value of the _symbol by the calculated pip value of the new trade
                # self.lot_size = self.calc_pip_value / self.pip_value
                self.lot_size = 0.1 * self.calc_pip_value / self.pip_value

            # Functionality for exotic pairs whose atr_in_pips may vary from the major pairs
            #a00 functionality for indices
            else:
                if self._symbol[3:] == 'JPY':
                    self.atr_in_pips = atr * 100

                    # Calculate the Pip Value based on the new trade to be taken, ie.
                    # Relating the risked amount (%Risk) to the risked pips (factor * ATR_in_pips) 
                    self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)

                    #To get the lot size, divide the current pip value of the
                    # _symbol by the calculated pip value of the new trade
                    self.lot_size = 0.1 * self.calc_pip_value / self.pip_value * 0.01

                elif self._symbol[3:] == 'SEK' or self._symbol[3:] == 'ZAR':
                    self.atr_in_pips = atr * 1000

                    # Calculate the Pip Value based on the new trade to be taken, ie.
                    # Relating the risked amount (%Risk) to the risked pips
                    # (factor * ATR_in_pips) 
                    self.calc_pip_value = self.risk_amount / (self.atr_in_pips * self.sl_multiplier)


                    #To get the lot size, divide the current pip value of the _symbol
                    # by the calculated pip value of the new trade
                    self.lot_size = self.calc_pip_value / self.pip_value

            self.stop_loss = self.calc_SL(atr)
            self.take_profit = self.calc_TP(atr)

        except Exception as e:
            print(e)

    # calculate Stop Loss
    #A00 add functionality depending on whether trade is sell or buy, ie using buy or sell value?
    def calc_SL(self, atr):
        # SL calculated as 1.5x of ATR
        if self._order == 'BUY':
            stop_loss_pips = self._symbol_ask - self.sl_multiplier * atr

        else:
            stop_loss_pips = self._symbol_bid + self.sl_multiplier * atr

        return stop_loss_pips
        

    # Calculate Take Profit
    def calc_TP(self, atr):

        if self._order == 'BUY':
            take_profit_pips = self._symbol_ask + self.tp_multiplier * atr

        else:
            take_profit_pips = self._symbol_bid - self.tp_multiplier * atr

        return take_profit_pips
        # TP calculated as 1.5x of ATR


    # Collect bid & ask prices of specific symbol after downloading current rates
    def bid_ask_price(self, _symbol):

        self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(_symbol)
        time.sleep(1)
        
        self.ZMQ_._DWX_MTX_SEND_TRACKPRICES_REQUEST_([_symbol])

        #Pause to allow Market DB to be updated with recent values
        time.sleep(1)

        # Get last item in the dict for the symbol
        _symbol_bid, _symbol_ask = list(self.ZMQ_._Market_Data_DB[_symbol].values())[-1]

        self.ZMQ_._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()
        self.ZMQ_._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()

        return _symbol_bid, _symbol_ask

    # Create process that monitors specific trade scenarios.
