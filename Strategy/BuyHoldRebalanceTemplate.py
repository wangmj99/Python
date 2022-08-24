from xmlrpc.client import DateTime
from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging

"""
Template for giving a list of stocks, generate portfolio weights per Strategy, calc pnl and performance
"""
class LastTradeInfo:
    def __init__(self) -> None:
        self.daysSinceLastTrade = 0
        self.transTable = {} #dictionary record last trades info, symbol and price pair

class BuyHoldRebalanceTemplate:
    dailyRet_label = 'dailyRet'

    def __init__(self, symbols:list , cooldowndays = 0, leverage =1):
        self.symbols =list(map(str.upper, symbols))
        self.leverage = leverage
        self.cooldowndays = cooldowndays  #cooldowndays after previous trade, to avoid frequent trades
        self.lastTrade = LastTradeInfo() 

    def backTest(self, startDate: datetime, endDate: datetime):
        """
        1. Get history data for all symbols
        2. Generate weight table
        3. Generate performance measure
        """
        logging.info('---------------------------------------Start BackTest--------------------------------------')
        mkd = retreiveEquityAdjCloseTable(self.symbols, startDate, endDate)              
        wts = pd.DataFrame(columns=self.symbols)
        self.BuildWeightsTable(mkd, wts)
        
        dailyRet= GetDailyPnlFromPriceAndWeightChg(mkd[self.symbols], wts).rename(BuyHoldRebalanceTemplate.dailyRet_label)
        res=pd.concat([mkd, dailyRet], axis = 1, join = 'inner')

        wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))
        res.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        return res

    @abstractmethod
    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame):
        pass
    
    @abstractmethod
    def ShowPerformance(self, testResult:pd.DataFrame, benchmark:str = None):
        pass

    def ShowBenchmarkPerformance(self, benchmark:str, startDate: datetime, endDate: DateTime):
            benchmark = str.upper(benchmark)
            benchmarkprice = retreiveEquityAdjCloseTable([benchmark], startDate, endDate)
            tmp = benchmarkprice[benchmark].pct_change().fillna(0)
            perf = PerfMeasure(tmp)
            perf.getPerfStats()
            logging.info('********************** Benchmark: {} sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4} totalReturn: {:.2%}, kellyWeight: {:.2%}'.
                format(benchmark, perf.sharpie, perf.mean, perf.std, perf.totalReturn, perf.kellyWeight))
            return perf
        





