from FinUtil import *
from MarketDataMgr import *
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import logging

"""
Template for giving a list of stocks, generate portfolio weights per Strategy, calc pnl and performance
"""
class LastTradeInfo:
    def __init__(self) -> None:
        self.daysSinceLastTrade = 0
        self.transTable = {} #dictionary record last trades info, symbol and price pair

class Tradesignal:
    def __init__(self) -> None:
        self.weights = {} #Symobl and new weight
        self.HasTradeSignal = False
        self.status = {} #Statistics along with signal, e.g. Zscore, Moveing Avg

class AbstractStrategy:
    dailyRet_label = 'dailyRet'

    def __init__(self, symbols:list , cooldowndays = 0, leverage =1, warmupDays = 0):
        self.symbols =list(set(map(str.upper, symbols)))
        self.leverage = leverage
        self.cooldowndays = cooldowndays  #cooldowndays after previous trade, to avoid frequent trades
        self.warmupDays = warmupDays # additional days of market data to prepare for certain algos using rolling window
        self.lastTrade = LastTradeInfo() 

    def backTest(self, startDate: datetime, endDate: datetime, getMktDataCSV = True):
        """
        1. Get history data for all symbols
        2. Generate weight table
        3. Generate performance measure
        """
        logging.info('---------------------------------------Start BackTest--------------------------------------')   
        warmstartDate = startDate if self.warmupDays == 0 else startDate - timedelta(days=self.warmupDays*2+3) 

        mkd = MarketDataMgr.getEquityDataSingleField(self.symbols, MarketDataMgr.adjcls_lbl, warmstartDate, endDate, getMktDataCSV)       
        wts = pd.DataFrame(columns=self.symbols)
        self.BuildWeightsTable(mkd, wts, startDate, endDate)
        
        dailyRet= GetDailyPnlFromPriceAndWeightChg(mkd[self.symbols], wts).rename(AbstractStrategy.dailyRet_label)
        res=pd.concat([mkd, dailyRet], axis = 1, join = 'inner')

        #wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))
        #res.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        return res, wts

    @abstractmethod
    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame, startDate: datetime, endDate: datetime):
        pass
    
    @abstractmethod
    def ShowPerformance(self, testResult:pd.DataFrame, benchmark:str = None):
        pass

    def ShowBenchmarkPerformance(self, benchmark:str, startDate: datetime, endDate: datetime):
            benchmark = str.upper(benchmark)
            benchmarkprice = MarketDataMgr.getEquityDataSingleField([benchmark], MarketDataMgr.adjcls_lbl, startDate, endDate)
            tmp = benchmarkprice[benchmark].pct_change().fillna(0)
            perf = PerfMeasure(tmp)
            perf.getPerfStats()
            logging.info('********************** Benchmark: {} sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4} totalReturn: {:.2%}, kellyWeight: {:.2%}'.
                format(benchmark, perf.sharpie, perf.mean, perf.std, perf.totalReturn, perf.kellyWeight))
            return perf
    
    def CreateLogEntry(self, symbols, dataSet, wts, index):
        wtsStrs, priceStrs = [], []
        for symbol in symbols:
            wtsStrs.append('{0}: {1:.0%} '.format(symbol, wts.loc[index, symbol]))
            priceStrs.append('{0}: {1}'.format(symbol, str(round(dataSet.loc[index, symbol],2))))
        
        res = 'Entry date: {0}, prices: {1} , weights: {2}'.format(
                pd.to_datetime(index).strftime('%m-%d-%Y'), 
                ", ".join(priceStrs), 
                ", ".join(wtsStrs))
        return res
    
    '''
    Check if algo create trade signal, buy/sell equities
    '''
    def EvalTradeSignal(self):
        pass





