import sys
import pandas as pd
import pandas_ta as ta
# from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector


#converting data formats

class data_manipulation():
    def __init__(self, data):
        if isinstance(data, list):      #instance of list expected when data has just been received from zmq server.
           
            data = pd.DataFrame.from_dict(data)

            data = data.drop(columns = ['spread', 'real_volume']) #columns contain only zeroes
            
            data_df = pd.DataFrame.from_dict(data)
            
            data_df['atr'] = data_df.ta.atr(length = 14)
            
            self.data_df = data_df

        
            #ATR will be included in each created DataFrame due to it's necessity in Risk Management.

    # Calculate RSI Value
    def calculate_rsi(self):
        rsi_df = self.data_df.ta.sma()




#Create trading strategies based on the data

# pandas DataFrame

# Calculate pandas_tas

# append

# remove nulls

#ADD monitoring of pairs for future time intervals

