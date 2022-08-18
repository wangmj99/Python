from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from BuyHoldRebalanceTemplate import *

class MultipleAssetPeriodRebalance(BuyHoldRebalanceTemplate):

    logging.basicConfig(filename="./logs/MultipleAssetPeriodRebalance.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    
    def __init__(self, symbols: list, equityRatio: list , cooldowndays=0, leverage=1 ):
        super().__init__(symbols, cooldowndays, leverage)
        self.equityRatio = equityRatio

        if len(symbols) == 0 or len(symbols)!= len(equityRatio):
            logging.error('equityRation size: {0} does not match input symbol size: {1}'.format(len(equityRatio), len(symbols)))
            raise ValueError('equityRation size: {0} does not match input symbol size: {1}'.format(len(equityRatio), len(symbols)))
    
    def BuildWeightsTable(self, mkd: pd.DataFrame, wts: pd.DataFrame):
        for index, row in mkd.iterrows():
            if self.lastTrade.daysSinceLastTrade > 0 and self.lastTrade.daysSinceLastTrade <= self.cooldowndays:
                self.lastTrade.daysSinceLastTrade+=1
                continue
            
            wts.loc[index] = self.equityRatio
            self.lastTrade.daysSinceLastTrade = 1

            #build log string
            wtsStrs, priceStrs = [], []
            for symbol in self.symbols:
                wtsStrs.append(symbol+': ')
                wtsStrs.append('{:.0%} '.format(wts.loc[index][symbol]))
                priceStrs.append(symbol+' price: ')
                priceStrs.append(str(round(row[symbol],2))+ ' ')
            
            logging.info("Entry date: {0}, rebalance {1} , wts: {2}".
                format(index.strftime('%m-%d-%Y'), 
                    "".join(priceStrs), 
                    "".join(wtsStrs))
            )

    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[BuyHoldRebalanceTemplate.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean: {:.4}, std: {:.4}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
        
        if benchmark != None:
            self.ShowBenchmarkPerformance(benchmark, res.index[0], res.index[-1])

        plotTwoYAxis([res[self.symbols[0]]], [perf1.statsTable['cumret']])

testcase = MultipleAssetPeriodRebalance(['spy','agg', 'iwm'], [0.6, 0.2, 0.2], 63, 1)
res = testcase.backTest(datetime(2012,1,1), datetime(2022,12,31))
testcase.ShowPerformance(res, 'spy')
