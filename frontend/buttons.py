from ast import Call
from .ui_manipulation import CallUi


class Button(CallUi):
    def __init__(self):
        super().__init__()
        

    def connect_button(self):
        self.ui.INIT_CONNECTOR_BTN.clicked.connect(
            self.backend_mt5.get_current_trades
            )

        self.ui.SEND_HIST_REQUEST_BTN.clicked.connect(
            self.backend_mt5.send_hist_request
            )

        self.ui.PREPARE_NEW_TRADE_BTN.clicked.connect(
            self.prepare_new_trade
            )

        self.ui.EXECUTE_NEW_TRADE_BTN.clicked.connect(
            self.execute_new_trade
            )

        self.ui.SELL_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_BTN))

        self.ui.BUY_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_BTN))

        self.ui.BUY_LIMIT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.BUY_LIMIT_BTN))

        self.ui.SELL_LIMIT_BTN.clicked.connect(
            lambda: self.order_type_btn_clicked(self.ui.SELL_LIMIT_BTN))

        self.ui.TWO_WAY_SPLIT_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.TWO_WAY_SPLIT_TRADE_BTN))

        self.ui.THREE_WAY_SPLIT_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.THREE_WAY_SPLIT_TRADE_BTN))

        self.ui.SINGLE_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.SINGLE_TRADE_BTN))

        self.ui.MINIMAL_TRADE_BTN.clicked.connect(
            lambda: self.order_strategy_btn_clicked(self.ui.MINIMAL_TRADE_BTN)
        )

        self.ui.MIN_1_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_1_BTN)
        )

        self.ui.MIN_5_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_5_BTN)
        )

        self.ui.MIN_15_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_15_BTN)
        )

        self.ui.MIN_30_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_30_BTN)
        )

        self.ui.MIN_60_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_60_BTN)
        )

        self.ui.MIN_240_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_240_BTN)
        )

        self.ui.MIN_1440_BTN.clicked.connect(
            lambda: self.order_timeframe_btn_clicked(self.ui.MIN_1440_BTN)
        )


        self.ui.CURRENT_TRADES_TABLE.doubleClicked.connect(self.clicked_table)

