# FX_MT4_app
Windows-Python Application for carrying out trade orders &amp; account analysis

# Agenda
The purpose of the project is to create a GUI app that integrates with the MT4 app for account & trade management. 
The project is supported by the open source library [ZeroMQ][1] for port communications to the MT4 platform, & [Darwinex's][2] functional scripts for sending commands from Python scripts to an Expert Advisor loaded on the MT4 platform.

# Functionality
Expected to grow with time, the main areas of current focus:
1. Risk Management - To provide risk calculation mechanisms for new trades. This is purely opinionated based on my own structure of placing trades with viable ris ranges. the application is due to take into consideration:
  a. % Balance of account to be risked during any trade
  b. Determine lot sizes to ensure balanced margin capacities for instruments with different risk thresholds
  c. Determine Stop Loss & Take Profit values based on the instrument's ATR value
  
2. Trade Placement, Updating, Deletion - In comparison to MT4's procedure of carrying out these tasks, it's intended that the application will allow for quicker manipulation once a solid workflow is developed.
3. Trade Performance Evaluation
4. Trade monitoring



[1]: https://zeromq.org
[2]: https://github.com/darwinex/dwx-zeromq-connector
