import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Slot, Qt
from DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx
import pandas as pd
import time

class DwxModel():

    def __init__(self):
        self.ZMQ_ = dwx()

        
        
    @Slot()
    def say_hello():
        print('Button Press recognized.')



    @Slot()
    def subscribe_marketdata(self, list_of_pairs):
        for pair in list_of_pairs:
            #subscribe to Pairs in List
            self.ZMQ_._DWX_MTX_SUBSCRIBE_MARKETDATA_(pair)
            # print('Subscribed to {}'.format(pair))


    @Slot()
    def send_hist_request(self, hist_dict_request):
        if len(hist_dict_request) == 0:
            return print('Empty Request.')
        for request in hist_dict_request:
            _symbol = request['_symbol']
            _timestamp = request.get('_timestamp', 15)
            _start = request.get('_start', '2022.01.01 00.00.00')
            _end = request.get('_end',pd.Timestamp.now().strftime('%Y.%m.%d %H.%M.00'))
            #check whether the item has valid data
            #is pair valid
            # is timeframe int? otherwise show 15 min data. Or other default value?
            # Automatically select start period? No. Should be provided, but automatically selected in the application.
            #end time would always be now.
            self.ZMQ_._DWX_MTX_SEND_HIST_REQUEST_(_symbol, _timestamp, _start, _end)
            time.sleep(0.0005)
