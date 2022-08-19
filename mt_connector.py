"""
Functionality to load the connection to the
MT4 or MT5 platform that is currently active.

The functionality places higher priority to the MT5 Python API,
then dwx_connect EA, finally the dwx_zmq EA.
Documentation to the Connection methods:
MT5 Python API: https://www.mql5.com/en/docs/integration/python_metatrader5
dwx_connect: https://github.com/darwinex/dwxconnect
dwx_zmq: https://github.com/darwinex/dwx-zeromq-connector
"""

#----------------------------21st May 2022------------------------------
#Major reform was set up. The application was shifted to
#specifically utilize the MT5 platform by the developer.
#Utilizing the dwx_MT4 connectors have been commented out below & can
# be enabled who would wish to make use of MT4 functionality.
# Onwards, the developemnt was done with only MT5 application
# 
# Contact teddywaweru@gmail.com if you require any assistance in re-enabling
# MT4 functionality.
# 
#---------------------------------------------------------------------------------  



# pylint: disable=no-member
import time
# from os.path import exists
# print('{}: Started loading dwx_connector file'.format(time.asctime(time.localtime())))
# Load the dwx_zmq object
# Load the dwx_connect object
# from dwx_connect.api.dwx_client import dwx_client
# print('{}: Finished loading DWX cONN Imports'.format(time.asctime(time.localtime())))
# from dwx_zmq.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector as dwx_zmq
# print('{}: Finished loading DWX_ZeroMQ cONN Imports'.format(time.asctime(time.localtime())))

# import dwx_MVC
# print('{}: Finished loading dwx_MVC'.format(time.asctime(time.localtime())))

print('{}: Start loading mt5_conn'.format(time.asctime(time.localtime())))
import mt5_conn
print('{}: Finished loading mt5_conn'.format(time.asctime(time.localtime())))

import MetaTrader5 as mt5
print('{}: Finished loading mt5'.format(time.asctime(time.localtime())))



#function order of preference for connecting to the MT4/ MT5 platforms:
# 1. MT5 API
# 2. DWX Client Connect MT5
# 3. DWX_ZMQ Client MT4


async def connect_mt():
    """_summary_
    """
    if mt5.initialize():
        return mt5, mt5_conn.Mt5Mvc(mt5)


    else:
        print('MT5 has not been initialized.')
        mt5.shutdown()





        #For the dwx_connect EA, the folder location of the active platform is
        #required. FOLDER_LIST shall contain user imputed list of possible folders
        #where the EA may be located.
        # FOLDERS_LIST = [
        #             'C:/Users/teddy/AppData/Roaming/MetaQuotes/Terminal/3294B546D50FEEDA6BF3CFC7CF858DB7/MQL4/Files/',
        #             'C:/Users/teddy/AppData/Roaming/MetaQuotes/Terminal/73B7A2420D6397DFF9014A20F1201F97/MQL5/Files/'
        #         ]
        #Iterate through the list of platform folders
        # for folder in FOLDERS_LIST:
        #     try:
        #         dwx = dwx_client(metatrader_dir_path=folder)

        #     #Capture exception
        #     except Exception as ex:
        #         _exstr = "Exception Type {0}. Args:\n{1!r}"
        #         _msg = _exstr.format(type(ex).__name__, ex.args)
        #         print(_msg)
        #         continue

        #     #Check if orders.txt file exists. File is only available if the EA is active
        #     #it's anticipated that only a single instance of dwxconnect is running, & the
        #     #first one detected shall be the one to use
        #     if exists(dwx.path_orders):
        #         dwx_mvc = dwx_MVC.DwxConnModel(dwx = dwx)
        #         break
        #     else:
        #         dwx = None

        # if no dwx_connect EA instance is detected, default back to ZeroMQ Connector
        # NOTE that there is no confirmation on whether there exists an instance
        # of the dwx_zmq EA running on the platform. The class however offers
        # its own form of error handling
        # if dwx is None:
        #     dwx = dwx_zmq()
        #     dwx_mvc = dwx_MVC.DwxZmqModel(dwx = dwx)

        # return dwx, dwx_mvc



