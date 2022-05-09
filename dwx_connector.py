"""
Functionality to load the connection to the
MT4 or MT5 EA that is currently active.

The functionality places higher priority to the
dwx_connect EA over the dwx_zmq EA.
"""

# pylint: disable=no-member
import time
from os.path import exists
print('{}: Started loading dwx_connector file'.format(time.time()))
# Load the dwx_zmq object
# Load the dwx_connect object
from dwx_connect.api.dwx_client import dwx_client

print('{}: Finished loading DWX cONN Imports'.format(time.time()))
from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx_zmq
print('{}: Finished loading DWX_ZeroMQ cONN Imports'.format(time.time()))

import dwx_MVC

import mt5_conn

import MetaTrader5 as mt5


#For the dwx_connect EA, the folder location of the active platform is
#required. FOLDER_LIST shall contain user imputed list of possible folders
#where the EA may be located.
FOLDERS_LIST = [
            'C:/Users/teddy/AppData/Roaming/MetaQuotes/Terminal/3294B546D50FEEDA6BF3CFC7CF858DB7/MQL4/Files/',
            'C:/Users/teddy/AppData/Roaming/MetaQuotes/Terminal/73B7A2420D6397DFF9014A20F1201F97/MQL5/Files/'
        ]

#function order of preference for connecting to the MT4/ MT5 platforms:
# 1. MT5 API
# 2. DWX Client Connect MT5
# 3. DWX_ZMQ Client MT4
async def connect_dwx():
    """_summary_
    """
    if mt5.initialize():
        return mt5, mt5_conn.Mt5Mvc(mt5)


    else:
        print('MT5 has not been initialized.')
        mt5.shutdown()
        #Iterate through the list of platform folders
        for folder in FOLDERS_LIST:
            try:
                dwx = dwx_client(metatrader_dir_path=folder)

            #Capture exception
            except Exception as ex:
                _exstr = "Exception Type {0}. Args:\n{1!r}"
                _msg = _exstr.format(type(ex).__name__, ex.args)
                print(_msg)
                continue

            #Check if orders.txt file exists. File is only available if the EA is active
            #it's anticipated that only a single instance of dwxconnect is running, & the
            #first one detected shall be the one to use
            if exists(dwx.path_orders):
                dwx_mvc = dwx_MVC.DwxConnModel(dwx = dwx)
                break
            else:
                dwx = None

        # if no dwx_connect EA instance is detected, default back to ZeroMQ Connector
        # NOTE that there is no confirmation on whether there exists an instance
        # of the dwx_zmq EA running on the platform. The class however offers
        # its own form of error handling
        if dwx is None:
            dwx = dwx_zmq()
            dwx_mvc = dwx_MVC.DwxZmqModel(dwx = dwx)

        return dwx, dwx_mvc



