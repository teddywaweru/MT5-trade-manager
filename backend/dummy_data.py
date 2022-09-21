
class Dummy_MT5:
    def __init__(self) -> None:
         pass

    def __str__(self) -> str:
         return "Pre-configured Dummy MT5 API"
    
class Dummy_Symbols:
    def __init__(self) -> None:

        self.SYMBOL_GROUPS = ['FOREX', 'METALS', 'INDICES', 'COMMODITIES', 'CRYPTO', 'ENERGIES', 'FUTURES']

        self.forex = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'AUDCAD', 'AUDCHF', 'AUDNZD', 'AUDSGD', 'EURAUD', 'EURCHF', 'EURGBP', 'GBPAUD', 'GBPCHF', 'NZDUSD', 'AUDJPY', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURCAD', 'EURJPY', 'EURNZD', 'GBPCAD', 'GBPJPY', 'GBPNZD', 'NZDJPY', 'CHFSGD', 'EURCZK', 'EURHUF', 'EURMXN', 'EURNOK', 'EURPLN', 'EURSEK', 'EURSGD', 'EURTRY', 'EURZAR', 'GBPMXN', 'GBPNOK', 'GBPSEK', 'GBPSGD', 'GBPTRY', 'NOKJPY', 'NOKSEK', 'NZDCAD', 'NZDCHF', 'SEKJPY', 'SGDJPY', 'USDCNH', 'USDCZK', 'USDHUF', 'USDMXN', 'USDNOK', 'USDPLN', 'USDRUB', 'USDSEK', 'USDSGD', 'USDTHB', 'USDTRY', 'USDZAR', 'ZARJPY', 'USDHKD']
        self.metals = [['XPDUSD', 'XPTUSD', 'Copper', 'Fortescue_Metals_(FMG.AX)', 'Metals_&_Mining_(XME.P)']]
        self.indices = ['AUS200', 'CN50', 'HK50', 'EUSTX50', 'FRA40', 'JPN225', 'NAS100', 'SPA35', 'UK100', 'US2000', 'US30', 'US500', 'USDX', 'SCI25', 'VIX', 'JPYX', 'EURX', 'CA60', 'CHINAH', 'NETH25', 'NOR25', 'SA40', 'SWI20', 'GERTEC30', 'MidDE50', 'GER40']
        self.stocks =  ['21st_Century_Fox_A_(FOXA.O)', '21st_Century_Fox_B_(FOX.O)', '3M_Company_(MMM.N)', 'A.O._Smith_Corp_(AOS.N)', 'AES_Corp_(AES.N)', 'AMC_Entertainment_(AMC.N)', 'AMETEK_Inc._(AME.N)', 'ANSYS_Inc._(ANSS.O)', 'APA_Corporation_(APA.O)', 'AT&T_Inc_(T.N)', 'AbbVie_Inc_(ABBV.N)', 'Abbott_Laboratories_(ABT.N)', 'Abiomed_Inc_(ABMD.O)', 'Accenture_PLC_(ACN.N)', 'Activision_Blizzard_(ATVI.O)', 'Adobe_Systems_Inc_(ADBE.O)', 'Adv._Micro_Devices_(AMD.O)', 'Advance_Auto_Parts_(AAP.N)', 'Aflac_Inc_(AFL.N)', 'Agilent_Technologies_(A.N)', 'Air_Products_&_Chemi_(APD.N)', 'Akamai_Technologies_(AKAM.O)', 'Alaska_Air_Group_Inc_(ALK.N)', 'Albemarle_Corp_(ALB.N)', 'Alcoa_Corporation_(AA.N)', 'Alexandria_Real_Est_(ARE.N)', 'Alibaba_Group_(BABA.N)', 'Align_Technology_(ALGN.O)', 'Allegion_(ALLE.N)', 'Alliant_Energy_Corp_(LNT.O)', 'Allstate_Corp_(ALL.N)', 'Alphabet_Inc_A_(GOOGL.O)', 'Alphabet_Inc_C_(GOOG.O)', 'Altria_Group_Inc_(MO.N)', 'Amazon.com_Inc_(AMZN.O)', 'Amcor_plc_(AMCR.N)', 'Ameren_Corp_(AEE.N)', 'American_Airlines_(AAL.O)', 'American_Electric_(AEP.O)', 'American_Express_(AXP.N)', 'American_Int_Grp_(AIG.N)', 'American_Tower_Corp_(AMT.N)', 'American_Water_Works_(AWK.N)', 'Ameriprise_Financial_(AMP.N)', 'AmerisourceBergen_(ABC.N)', 'Amgen_Inc_(AMGN.O)', 'Amphenol_Corp_(APH.N)', 'Analog_Devices_(ADI.O)', 'Anthem_Inc_(ANTM.N)', 'Aon_plc_(AON.N)', 'Apple_Inc_(AAPL.O)', 'Applied_Materials_(AMAT.O)', 'Aptiv_PLC_(APTV.N)', 'ArcherDanielsMidland_(ADM.N)', 'Arista_Networks_(ANET.N)', 'Arthur_J_Gallagher_(AJG.N)', 'Assurant_(AIZ.N)', 'Atmos_Energy_(ATO.N)', 'Aurora_Cannabis_(ACB.N)', 'AutoZone_Inc_(AZO.N)']
        self.commodities =  ['XAGEUR', 'XAGUSD', 'XAGAUD', 'XAUAUD', 'XAUEUR', 'XAUUSD', 'Cocoa', 'Coffee', 'Cotton', 'Sugar', 'Soybeans', 'Wheat', 'SpotBrent', 'SpotCrude', 'XAUGBP', 'XAUCHF', 'XAUJPY', 'XPDUSD', 'XPTUSD', 'Copper', 'NatGas', 'OJ', 'LDSugar', 'Lumber', 'Corn', 'LeanHogs', 'Cattle', 'Gasoline', 'Oats', 'SoyMeal', 'SoyOil', 'RghRice']
        self.crypto = [None]
        self.energies = ['SpotBrent', 'SpotCrude', 'NatGas', 'Gasoline', 'TotalEnergies_ADR_(TTE.N)']
        self.futures = [None
        ]
    def __str__(self) -> str:
         return "Pre-populated Dummy_Symbols"

