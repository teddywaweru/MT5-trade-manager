## Meta Trader 5 Trade Manager

The GUI application is intended to be used for facilitating trades in the MT5 platform. The application utilizes the Python API of the platform to carry out client requests. There will be need to expand functionality to include MQL4 & MQL5 scripts, as the API is still not mature enough.

![Image](images/MT5_TradeManager_GUI.png)

---
## Expectations

Expected to grow with time, the main areas of current focus:

Risk Management - To provide risk calculation mechanisms for new trades. This is purely opinionated based on my own structure of placing trades with viable ris ranges. the application is due to take into consideration: a. % Balance of account to be risked during any trade b. Determine lot sizes to ensure balanced margin capacities for instruments with different risk thresholds c. Determine Stop Loss & Take Profit values based on the instrument's ATR value

Trade Placement, Updating, Deletion - In comparison to MT4's procedure of carrying out these tasks, it's intended that the application will allow for quicker manipulation once a solid workflow is developed.

Trade Performance Evaluation

Trade monitoring
