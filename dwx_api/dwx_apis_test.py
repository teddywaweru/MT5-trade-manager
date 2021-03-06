# Let's import the different classes:
from darwinexapis.API.InfoAPI.DWX_Info_API import DWX_Info_API
from darwinexapis.API.InvestorAccountInfoAPI.DWX_AccInfo_API import DWX_AccInfo_API
from darwinexapis.API.QuotesAPI.DWX_Quotes_API import DWX_Quotes_API
from darwinexapis.API.TradingAPI.DWX_Trading_API import DWX_Trading_API
from darwinexapis.API.WebSocketAPI.DWX_WebSocket_API import DWX_WebSocket_API

### Let's create the authentication dictionary:
AUTH_CREDS = {'access_token': '8678ab04-31ad-3c97-9c15-39378989904d',
              'consumer_key': 'rIh1TMvXMNwZEjTiuUb6SnY5hMEa',
              'consumer_secret': 'ZiV5263YLSUPaDV32ij39KGDDPYa',
              'refresh_token': '4811cde8-b403-3b89-ba15-f63c9553ecee'}

# Let's instantiate some API objects:
darwinexInfo = DWX_Info_API(AUTH_CREDS, _version=2.0, _demo=True)
darwinexInvestorAcc = DWX_AccInfo_API(AUTH_CREDS, _version=2.0, _demo=True)
darwinexQuotes = DWX_Quotes_API(AUTH_CREDS, _version=1.0)
darwinexTrading = DWX_Trading_API(AUTH_CREDS, _version=1.1, _demo=True)
darwinexWebSocket = DWX_WebSocket_API(AUTH_CREDS, _version=0.0)

# DWX_Info_API:
darwinUniverse = darwinexInfo._Get_DARWIN_Universe_(_status='ACTIVE',
                                                    _iterate=True,
                                                    _perPage=100)
print(darwinUniverse)

# DWX_AccInfo_API:
print(darwinexInvestorAcc._Get_Accounts_())

# DWX_Quotes_API:
darwinexQuotes._stream_quotes_()
darwinexQuotes._process_stream_(_symbols=["ENH.4.16"],
                                _plot=False)

# DWX_Trading_API:
print(darwinexTrading._Get_Permitted_Operations_())
print(darwinexTrading._Get_Account_Leverage_(_id=0))

# DWX_WebSocket_API:
darwinexWebSocket.run(_symbols=["ENH.4.16",
                                "CIS.4.11",
                                "CGT.4.5",
                                "CDG.4.14",
                                "ABH.4.21",
                                "ENO.4.13"])