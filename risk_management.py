import pandas as pd


# Calculate risk
class risk_management():
    def __init__(self, ZMQ_, risk, account_info, new_trade_df, hist_db_key):
        self.risk = None
        self.ZMQ_ = ZMQ_
        self.account_balance = account_info['_data']['accountbalance']
        self._symbol = hist_db_key[:6]
        self._timeframe = hist_db_key[7:]
        
        self.sec_symbol = None

        #Major Currency pairs, where USD is the secondary currency traded.
        self.major_curr = ['AUD', 'EUR', 'GBP', 'NZD']



    # Calculate Margin based on Risk & Stop Loss
    # The formula for calculation is as:
    # Risk amount / Stop Loss Value = Pip Value. This was obtained from the NNFX Trading strategy:
    # https://www.youtube.com/watch?v=bqWLFNpK6eg&t=1161s  
    def calc_lot(self):

        #check whether USD is part of the currency pair ('USD' since this is the account currency)
        if 'USD' not in self._symbol:

            #Check whether _symbol contains one of the major pairs (where USD is the secondary currency.)
            if self._symbol[:3] in self.major_curr:
                
                self.sec_symbol = self._symbol[:3] + 'USD'

                #Subscribe to market data
                self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(self._symbol)
                self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(self.sec_symbol)


                #Collect bid/ask prices on major pairs

            # determine instrument to be downloaded
            # ie. is USD at the start or at the back

            # Download the bid/ask price



    # calculate Stop Loss
    def calc_SL(self):
        pass
        
        

    # Calculate Take Profit
    def calc_TP(self):
        pass


    # Create process that monitors specific trade scenarios.

