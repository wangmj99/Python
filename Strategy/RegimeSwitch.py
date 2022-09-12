from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from BuyHoldRebalanceTemplate import *

"""
predict regime switch of the stock if it's down x% from N-day high or up x% from N-day low, then short/long and hold for Y days.
parameters will be 1. pct of down/up from high/low, 2. N days low/high, 3. holding period Y 
"""
class RegimeSwitch(BuyHoldRebalanceTemplate):
    logging.basicConfig(filename="./logs/RegimeSwitch.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    
    

    def __init__(self, symbols: list, ndays,  pctChg, holdDays, cooldowndays=0, leverage=1):
        super().__init__(symbols, cooldowndays, leverage)
        self.ndays = ndays
        self.pctChg = abs(pctChg)/100
        self.holdDays = holdDays
        self.warmupDays = ndays

    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame, startDate: datetime, endDate: datetime):
        tradeSignal = 'Signal'
        self.lastTrade.transTable = {tradeSignal : 0} # 1 long , -1 short , 0 no postion
        
        symbol = str.upper(self.symbols[0])
        highs = mkd[symbol].rolling(self.ndays).max()
        lows = mkd[symbol].rolling(self.ndays).min()

        mkd['high'] = highs
        mkd['low'] = lows

        mkd = mkd.dropna()
        mkd = mkd.loc[startDate: endDate]

        wts.loc[mkd.index[0]] = [0]

        for idx, row in mkd.iterrows():
            flag = False
            if len(self.lastTrade.transTable) >0  and self.lastTrade.daysSinceLastTrade <= self.cooldowndays: # still in cooldownday:
                self.lastTrade.daysSinceLastTrade +=1
                continue

            #if pass holding period, close position
            if self.lastTrade.daysSinceLastTrade >= self.holdDays and self.lastTrade.transTable[tradeSignal] != 0:
                wts.loc[idx] = [0]
                self.lastTrade.transTable[tradeSignal] = 0
                flag = True
                
            else:
                #if up certain pct from ndays low, go long:
                if self.lastTrade.transTable[tradeSignal] == 0:
                    if row[symbol] >= row['low']*(1+self.pctChg):
                        wts.loc[idx] = [1]
                        self.lastTrade.transTable[tradeSignal] = 1
                        flag = True
                    elif row[symbol] <= row['high']*(1-self.pctChg):
                        wts.loc[idx] = [-1]
                        self.lastTrade.transTable[tradeSignal] = -1
                        flag = True
                elif self.lastTrade.transTable[tradeSignal] == 1: # long position
                    if row[symbol] <= row['high']*(1-self.pctChg):
                        wts.loc[idx] = [-1]
                        self.lastTrade.transTable[tradeSignal] = -1
                        flag = True
                else: # hold short position
                    if row[symbol] >= row['low']*(1+self.pctChg):
                        wts.loc[idx] = [1]
                        self.lastTrade.transTable[tradeSignal] = 1
                        flag = True

            if flag == True:
                self.lastTrade.daysSinceLastTrade = 1
                actionstr = actionStr = 'Exit Trade' if wts.loc[idx, symbol]==0 else ('Enter long trade' if wts.loc[idx, symbol]==1 else 'Enter short trade' )
                logging.info('{0}, action: {1}'. format(self.CreateLogEntry(self.symbols, mkd, wts, idx), actionStr))
            else:
                self.lastTrade.daysSinceLastTrade+=1


    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[BuyHoldRebalanceTemplate.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
        #plotTwoYAxis([res[BuyHoldwithMAV.mv_label],res[self.symbols[0]]], [perf1.statsTable['cumret']])

        if benchmark != None:
            self.ShowBenchmarkPerformance('spy',res.index[0], res.index[-1])

testcase = RegimeSwitch(['MDY'], 20, 5, 21)
res = testcase.backTest(datetime(2022,1,1), datetime(2022,9,10))
testcase.ShowPerformance(res[0], 'SPY')
