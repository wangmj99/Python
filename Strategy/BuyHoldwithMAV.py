from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from BuyHoldRebalanceTemplate import *

"""
Long stock1 if above moving average, long stock2 if stock1 is below moving average
"""
class BuyHoldwithMAV(BuyHoldRebalanceTemplate):
    mv_label = 'MV_AVG'
    logging.basicConfig(filename="./logs/BuywithMV.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    

    def __init__(self, symbols: list, cooldowndays=0, leverage=1, movingWindow = 50):
        super().__init__(symbols, cooldowndays, leverage)
        self.window = movingWindow
        
    
    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame):
        rolling = mkd[self.symbols[0]].rolling(self.window)
        mv_avg = rolling.mean().shift(1) 

        stock1, stock2, mvg = self.symbols[0], self.symbols[1], BuyHoldwithMAV.mv_label
        
        mkd[mvg] = mv_avg
        mkd = mkd.dropna()
        
        for index, row in mkd.iterrows():
            if len(self.lastTrade.transTable) >0  and self.lastTrade.daysSinceLastTrade <= self.cooldowndays: # still in cooldownday:
                self.lastTrade.daysSinceLastTrade +=1
                continue

            flag = False
            if row[stock1] >= row[mvg] and (
                    len(self.lastTrade.transTable) ==0 or self.lastTrade.transTable[stock1] < self.lastTrade.transTable[mvg]):
                wts.loc[index] = [1*self.leverage, 0]
                flag = True
            elif row[stock1] < row[mvg] and (
                    len(self.lastTrade.transTable) ==0 or self.lastTrade.transTable[stock1] >= self.lastTrade.transTable[mvg]):
                wts.loc[index] = [0, 1]
                flag = True
            
            if flag:
                wtsStr = '{}: {:.0%}, {}: {:.0%}'.format(stock1,wts.loc[index][stock1], stock2, wts.loc[index][stock2])
                logging.info("Entry date: {0}, rebalance  {1} price: {2}, mvg: {3}, {4} price: {5}, wts: {6}".
                format(index.strftime('%m-%d-%Y'), 
                    stock1, 
                    round(row[stock1],2), 
                    round(row[mvg],2), 
                    stock2, 
                    round(row[stock2],2), 
                    wtsStr))
                self.lastTrade.daysSinceLastTrade = 1
                self.lastTrade.transTable[stock1] = row[stock1], 
                self.lastTrade.transTable[mvg] = row[mvg]   
    
    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[BuyHoldRebalanceTemplate.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
        plotTwoYAxis([res[BuyHoldwithMAV.mv_label],res[self.symbols[0]]], [perf1.statsTable['cumret']])

        if benchmark != None:
            benchmark = str.upper(benchmark)
            benchmarkprice = retreiveEquityAdjCloseTable([benchmark], res.index[0], res.index[-1]) 
            perf2 = PerfMeasure(benchmarkprice[benchmark].pct_change().fillna(0))
            perf2.getPerfStats()
            logging.info('********************** Benchmark: {} sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4} totalReturn: {:.2%}'.format(benchmark, perf2.sharpie, perf2.mean, perf2.std, perf2.totalReturn))

testcase = BuyHoldwithMAV(['spy', 'tlt'], 20, 1, 50)
res = testcase.backTest(datetime(2007,1,1), datetime(2022,12,31))
testcase.ShowPerformance(res, 'spy')



