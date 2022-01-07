from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
import time
import pandas as pd
# from dwx_connector_MVC import DwxModel



# Calculate risk
class risk_management():

    
    def __init__(self, ZMQ_ = None, risk = None, account_info = None, new_trade_df = None, hist_db_key = None):
        
        if risk is None:
            risk = 0.02     # Default value for risk
        self.risk = risk
        if ZMQ_ is None:
            ZMQ_ = dwx()
        self.ZMQ_ = ZMQ_
        self.new_trade_df = new_trade_df
        self.account_info = account_info
        self.hist_db_key = hist_db_key
        self._symbol = hist_db_key[:6]
        self._timeframe = hist_db_key[7:]
        
        self.sec_symbol = None

        #Major Currency pairs, where USD is the secondary currency traded.
        #ADD commodities ie XAG, XPT, XAU
        self.major_curr = ['AUD', 'EUR', 'GBP', 'NZD']

        # Exotic pairs whose values do not conform to typical 5 point values ie. SEK, JPY
        #ADD all necessary pairs to be considered
        self.exotic_curr = ['SEK', 'JPY', 'ZAR', 'XAG', 'XAU', 'XPT']



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s
    def calc_lot(self):

        try:
            #Subscribe to market data of _symbol
            self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(self._symbol)
            time.sleep(0.05)

            #Request for Current Tracked Prices.
            self.ZMQ_._DWX_MTX_SEND_TRACKPRICES_REQUEST_([self._symbol])
            time.sleep(2)

            #Allow time for the values to be loaded onto the Market_DB dict.

            bid_symbol, ask_symbol = self.bid_ask_price(self._symbol)

            #check whether USD is part of the currency pair ('USD' since this is the account currency)
            if 'USD' in self._symbol:
                
                if 'USD' in self._symbol[:3]:
                    pip_value = (bid_symbol + ask_symbol) / 2

                else:
                    pip_value = 1
            
            else:

                #Check whether _symbol contains one of the major pairs (where USD is the secondary currency.)
                #If first part of the symbol is a major currency pair ie. AUD, NZD, EUR, GBP...
                if self._symbol[3:] in self.major_curr:
                    
                    self.sec_symbol = self._symbol[3:] + 'USD'

                    # Collect bid/ask prices from Market_DB
                    bid_sec_symbol, ask_sec_symbol = self.bid_ask_price(self.sec_symbol)

                    pip_value = (bid_sec_symbol + ask_sec_symbol) / 2

                else:
                    self.sec_symbol = 'USD' + self._symbol[3:]

                    # Collect bid/ask prices from Market_DB
                    bid_sec_symbol, ask_sec_symbol = self.bid_ask_price(self.sec_symbol)

                    pip_value = 1 / ((bid_sec_symbol + ask_sec_symbol) / 2)

            #ATR value from dataframe
            atr = self.new_trade_df['atr'].iloc[-1]

            # Calculate risk amount of the accountbalance
            risk = self.account_info['_data']['accountbalance'] * self.risk


            # Calculate pip value for the trade ie. Pip = %Risk Acct. Amount / Risk Stop Loss
            #A00 add functionality for exotic pairs
            if self._symbol[:3] not in self.exotic_curr and self._symbol[3:] not in self.exotic_curr:

                atr_in_pips = atr * 10000

                # Calculate the Pip Value based on the new trade to be taken, ie.
                # Relating the risked amount (%Risk) to the risked pips (factor * ATR_in_pips) 
                calc_pip_value = risk / atr_in_pips

                #To get the lot size, divide the current pip value of the _symbol by the calculated pip value of the new trade
                lot_size = calc_pip_value / pip_value









            stop_loss = self.calc_SL(atr)
            take_profit = self.calc_TP(atr)
                #To Calculate Pip value, sec_symbol / _symbol.
                # ie. in AUDCAD, The pip value is calculated using the rate of AUDCAD / AUDUSD


                    #A00 Include circumstance for JPY & other unique pairs



                    #A00 Include circumstance for JPY & other unique pairs



                # Download the bid/ask price

        except Exception as e:
            print(e)

    # calculate Stop Loss
    #A00 add functionality depending on whether trade is sell or buy, ie using buy or sell value?
    def calc_SL(self, atr):
        # SL calculated as 1.5x of ATR

        #A00 functionality for accepting factor value from user
        factor = 1.5

        return factor * atr

        
        

    # Calculate Take Profit
    def calc_TP(self, atr):
        # TP calculated as 1x of ATR
        factor = 1

        #A00 functionality for accepting factor value from user
        return factor * atr

    # Collect bid & ask prices of specific symbol after downloading current rates
    def bid_ask_price(self, _symbol):

        
        self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(_symbol)
        time.sleep(0.05)
        
        self.ZMQ_._DWX_MTX_SEND_TRACKPRICES_REQUEST_([_symbol])

        #Pause to allow Market DB to be updated with recent values
        time.sleep(2)

        # Get last item in the dict for the symbol
        bid_symbol, ask_symbol = list(self.ZMQ_._Market_Data_DB[_symbol].values())[-1]

        self.ZMQ_._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()

        return bid_symbol, ask_symbol

    # Create process that monitors specific trade scenarios.

