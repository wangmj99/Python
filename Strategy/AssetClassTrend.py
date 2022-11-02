from calendar import month
from ntpath import join
from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from AbstractStrategy import *

"""
https://quantpedia.com/strategies/asset-class-trend-following/

Use 5 ETFs (SPY - US stocks, EFA - foreign stocks, IEF - bonds, VNQ - REITs, 
GSG - commodities), equal weight the portfolio. Hold asset class ETF only when 
it is over its 10 month Simple Moving Average, otherwise stay in cash.
"""

class AssetClassTrend(AbstractStrategy):
    mv_label = 'MV_AVG'
    logging.basicConfig(filename="./logs/AssetClassTrend.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    

    def __init__(self, symbols: list, cooldowndays=0, leverage=1,  movingWindow = 21*10):
        super().__init__(symbols, cooldowndays, leverage)
        self.window = movingWindow
        self.warmupDays = movingWindow
        
    
    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame, startDate: datetime, endDate: datetime):
        col = mkd.columns
        
        createmvlbl = lambda x: '{}_MV'.format(x)

        for symbol in col:
            rolling = mkd[symbol].rolling(self.window)
            mv_avg = rolling.mean().shift(1)
            lbl = createmvlbl(symbol)
            mkd[lbl] = mv_avg

        mkd = mkd.dropna()
        mkd = mkd.loc[startDate:endDate]

        trade_key, trade_date = "LastTrade", "LastTradeDate"

        for index, row in mkd.iterrows():
            if len(self.lastTrade.transTable) >0  and self.lastTrade.daysSinceLastTrade <= self.cooldowndays: # still in cooldownday:
                self.lastTrade.daysSinceLastTrade +=1
                continue
            
            # check and skip the same month
            if len(self.lastTrade.transTable) >0 and self.lastTrade.transTable[trade_date].month == index.month:
                continue
            
            longs = set()

            for symbol in col:
                mvlbl = createmvlbl(symbol)
                if row[symbol] >= row[mvlbl]:
                    longs.add(symbol)

            if len(self.lastTrade.transTable) > 0 and longs == set([ x for x in self.lastTrade.transTable[trade_key].keys() if self.lastTrade.transTable[trade_key][x][2] >0]):
                continue
           
            weight = 1/len(longs)*self.leverage if len(longs) > 0 else 0
            self.lastTrade.transTable.clear()
            self.lastTrade.transTable[trade_key] = {}
            self.lastTrade.transTable[trade_date] = index
            self.lastTrade.daysSinceLastTrade = 1

            logstr = []
            for symbol in col:
                val = weight*self.leverage if symbol in longs else 0
                wts.loc[index,symbol] = val 
                self.lastTrade.transTable[trade_key][symbol] = [row[symbol], row[createmvlbl(symbol)], val]
                if val != 0:
                    logstr.append('{} price: {}, mvg: {}, wts: {}'.format(symbol, round(row[symbol],2), round(row[createmvlbl(symbol)],2), round(val,2) ))
            
            if len(logstr) == 0: logstr.append('Exit all position')
            logging.info("Entry date: {0}, {1}".format(index.strftime('%m-%d-%Y'), '|'.join(logstr)))
          
    
    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[AbstractStrategy.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
        #plotTwoYAxis([res[AssetClassTrend.mv_label],res[self.symbols[0]]], [perf1.statsTable['cumret']])
        perf1.statsTable['cumret'].plot()
        plt.show()

        if benchmark != None:
            self.ShowBenchmarkPerformance('spy',res.index[0], res.index[-1])

testcase = AssetClassTrend(["SPY", "EFA", "IEF", "VNQ", "GSG"], 0, 1, 210)
#testcase = AssetClassTrend(["XLK", "XLV", "XLE", "XLY", "XLI", "XLRE", "XLP", "XLF", "XLC", "XLU", "XLB", "TLT", "DBC"], 0, 2, 210)
res = testcase.backTest(datetime(2020,1,1), datetime(2021,12,2))
testcase.ShowPerformance(res[0], 'SPY')



