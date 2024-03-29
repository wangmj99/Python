from datetime import date
from lib2to3.pygram import Symbols
from logging import lastResort
from signal import SIGABRT
from tempfile import tempdir
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
from FinUtil import *
from MarketDataMgr import *
from AbstractStrategy import * 
import traceback
from statsmodels.tsa.vector_ar.vecm import coint_johansen 
from statsmodels.tsa.stattools import coint 


class PairTrading(AbstractStrategy):
    spread_lbl, zscore_lbl, mean_lbl, std_lbl, beta_lbl, hldDur_lbl = 'spread', 'rollingZ', 'Mean', 'Std', 'Beta', 'HldingDur'
    tradeSignal = 'Signal'
    logging.basicConfig(filename="./logs/PairTrading.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    

    def __init__(self, symbols: list, cooldowndays=0, leverage=1, window = 50, stoploss = 100):
        super().__init__(symbols, cooldowndays, leverage)
        self.window = window
        self.warmupDays = window
        self.stoploss = -abs(stoploss/100)

    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame,startDate: datetime, endDate: datetime):
        #stoploss = self.stoploss
        s1, s2 = self.symbols[0], self.symbols[1]

        mkd[PairTrading.zscore_lbl] = 0.0
        mkd[PairTrading.spread_lbl] = 0.0
        mkd[PairTrading.mean_lbl]= 0.0
        mkd[PairTrading.std_lbl] = 0.0
        mkd[PairTrading.beta_lbl]= 0.0
        mkd[PairTrading.hldDur_lbl]= 0.0
        
        #wts= pd.DataFrame(columns=[s1, s2])
        upThld, lowThld = 1.65, 0.5
        
        self.lastTrade.transTable = {PairTrading.tradeSignal : 0} # 1 long spread, -1 short spread, 0 no postion

        #get the startdate index in the dataframe
        startIdx = mkd.index.get_loc(startDate, method='bfill') 

        endIdx = mkd.index.get_loc(endDate, method='ffill') 

        #mark the start position
        wts.loc[mkd.index[startIdx]] = [0,0]

        #for t in range(self.window-1, len(mkd)):
        #for t in range(startIdx, len(mkd)):
        for t in range(startIdx, endIdx+1):
            tmpdf = mkd.iloc[t-self.window+1:t+1]
            
            #s2 = smf.add_constant(s2)
            f = '{}~{}'.format(s1, s2)
            lm = smf.ols(formula=f, data=tmpdf).fit()
            
            tmpSprd = tmpdf[s1]-tmpdf[s2]*lm.params[1]
            zscore = (tmpSprd[-1] - tmpSprd.mean())/tmpSprd.std()

            idx = mkd.index.values[t]
            mkd.loc[idx, PairTrading.zscore_lbl] = zscore
            mkd.loc[idx, PairTrading.spread_lbl] = tmpSprd[-1]
            mkd.loc[idx, PairTrading.mean_lbl] = tmpSprd.mean()
            mkd.loc[idx, PairTrading.std_lbl] = tmpSprd.std()
            mkd.loc[idx, PairTrading.beta_lbl] = lm.params[1]

            if t-startIdx>=self.window:
                tmps = mkd[PairTrading.spread_lbl].iloc[t-self.window: t+1]
                holdTime = CalcHalfHoldingPeriod(tmps)
                mkd.loc[idx, PairTrading.hldDur_lbl] = holdTime
            
            flag = False

            if self.lastTrade.isStopLoss and self.lastTrade.daysSinceLastTrade <= self.cooldowndays:
                self.lastTrade.daysSinceLastTrade +=1
                logging.info('Still in the cooldown days after stoploss, Date: {}'.format(idx))
                continue

            if self.lastTrade.transTable[PairTrading.tradeSignal] == 0:
                if zscore >= upThld:
                    wts.loc[idx] = [-1, 1]
                    self.lastTrade.transTable[PairTrading.tradeSignal] = -1
                    self.lastTrade.transTable[s1] = mkd.loc[idx, s1]  #log transaction s1 price
                    self.lastTrade.transTable[s2] = mkd.loc[idx, s2]  #log transaction s2 price
                    self.lastTrade.isStopLoss = False
                    flag = True
                elif zscore <= -upThld:
                    wts.loc[idx] = [1, -1]
                    self.lastTrade.transTable[PairTrading.tradeSignal] = 1
                    self.lastTrade.transTable[s1] = mkd.loc[idx, s1]  #log transaction s1 price
                    self.lastTrade.transTable[s2] = mkd.loc[idx, s2]  #log transaction s2 price
                    self.lastTrade.isStopLoss = False
                    flag = True
            elif self.lastTrade.transTable[PairTrading.tradeSignal] == 1:
                if zscore >=-lowThld:
                    wts.loc[idx] = [0,0]
                    self.lastTrade.transTable[PairTrading.tradeSignal] = 0
                    del self.lastTrade.transTable[s1]  #remove s1 from lastTrade
                    del self.lastTrade.transTable[s2]  #remove s2 from lastTrade
                    self.lastTrade.isStopLoss = False
                    flag = True
            else: # tradeSignal == -1
                if zscore <= lowThld:
                    wts.loc[idx] = [0,0]
                    self.lastTrade.transTable[PairTrading.tradeSignal] = 0
                    del self.lastTrade.transTable[s1]  #remove s1 from lastTrade
                    del self.lastTrade.transTable[s2]  #remove s2 from lastTrade
                    self.lastTrade.isStopLoss = False
                    flag = True

            # check stop loss
            if self.stoploss > -1 and flag == False and self.lastTrade.transTable[PairTrading.tradeSignal] != 0:  
                
                tmpPerf =  self.GetPnlSinceLastTrade(self.lastTrade, mkd.loc[idx, s1], mkd.loc[idx, s2])
                if tmpPerf <= self.stoploss:
                    wts.loc[idx] = [0,0]
                    self.lastTrade.transTable[PairTrading.tradeSignal] = 0
                    self.lastTrade.isStopLoss = True
                    del self.lastTrade.transTable[s1]  #remove s1 from lastTrade
                    del self.lastTrade.transTable[s2]  #remove s2 from lastTrade
                    flag = True
                    logging.info('Stop loss triggered: loss: {:.2%}'.format(tmpPerf))
                
            if flag == True:
                self.lastTrade.daysSinceLastTrade = 1
                actionstr = actionStr = 'Enter Trade' if wts.loc[idx, s1]!=0 else 'Exit Trade'
                logging.info('{0}, action: {1}'. format(self.CreateLogEntry(self.symbols, mkd, wts, idx), actionStr))
                
                logging.info('--------> zscore: {0}, mean: {1}, std: {2}'.format(
                    mkd.loc[idx][PairTrading.zscore_lbl], 
                    mkd.loc[idx][PairTrading.mean_lbl], 
                    mkd.loc[idx][PairTrading.std_lbl]))
            else:
                self.lastTrade.daysSinceLastTrade+=1
                    

        wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts_({}, {})'.format(s1, s2)))
        mkd.to_csv(MarketDataMgr.dataFilePath.format('tmp_({}, {})'.format(s1, s2)))
        
    def GetPnlSinceLastTrade(self, lastTrade: LastTradeInfo, s1price, s2price):
        s1, s2 = self.symbols[0], self.symbols[1]
        s10Price, s20Price = lastTrade.transTable[s1], lastTrade.transTable[s2]
        s1perf = s1price/s10Price -1
        s2perf = s2price/s20Price -1
        res = lastTrade.transTable[PairTrading.tradeSignal] *(s1perf - s2perf)
        return res

    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[AbstractStrategy.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}, KellyWeight: {:.2%}'.
        format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn, perf1.kellyWeight/2))
        plotTwoYAxis([res[PairTrading.spread_lbl]], [perf1.statsTable['cumret']])

        res[PairTrading.beta_lbl].plot()

        if benchmark != None:
            self.ShowBenchmarkPerformance(benchmark,res.index[0], res.index[-1])

    
    def EvalTradeSignal(self):
        now = datetime.now()
        endDate = datetime(now.year, now.month, now.day)
        #endDate = datetime(2022,7,8)
        signal = Tradesignal()
        res, wts = self.backTest(datetime(2022,1,1), endDate)
        if self.lastTrade.daysSinceLastTrade == 1:
            signal.HasTradeSignal = True
            tmp = {}
            for symbol in wts.columns:
                tmp[symbol] = wts.loc[endDate, symbol]
            signal.weights = tmp
        lastDateEntry = res.index[-1]
        signal.status[PairTrading.zscore_lbl] = res.loc[lastDateEntry, PairTrading.zscore_lbl]
        signal.status[self.symbols[0]] = res.loc[lastDateEntry, self.symbols[0]]
        signal.status[self.symbols[1]] = res.loc[lastDateEntry, self.symbols[1]]
        
          
        return signal
    
    @staticmethod
    def PrepareData(symbols:list, startDate: datetime, endDate: datetime, warmupWindow: int):
        warmstartDate = startDate - timedelta(days=warmupWindow*2+3) 
        MarketDataMgr.retrieveHistoryDataToCSV(symbols, warmstartDate, endDate)

    @staticmethod
    def RunSymbolMatrixTest(symbols: list, startDate: datetime, endDate: datetime, windowTest: int, retrieveMktData: bool):
        cooldownTest, leverageTest = 0, 1

        perfRes = []
        for idx1 in range(len(symbols)):
            for idx2 in range(idx1+1, len(symbols)):
                s1, s2 = symbols[idx1], symbols[idx2]
                if s1 == s2: continue
                testcase = PairTrading([s1, s2], cooldownTest, leverageTest, windowTest)
                res, wts = testcase.backTest(startDate, endDate, retrieveMktData)
                perfTest = PerfMeasure(res[AbstractStrategy.dailyRet_label])
                perfTest.getPerfStats()
                logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}, KellyWeight: {:.2%}'.
                format(perfTest.sharpie, perfTest.mean, perfTest.std, perfTest.totalReturn, perfTest.kellyWeight/2))
                tup = (s1, s2, perfTest)
                perfRes.append(tup)
        

        perfRes.sort(key = lambda x: x[2].totalReturn,  reverse= True)
        logging.info('Matrix Result Timeframe: {} to {}'.format(startDate, endDate))
        for i in range(0, min(10, len(perfRes))):
            item = perfRes[i]
            logging.info('Matrix Result: {0}, {1}, return: {2:.2%}, sharpie: {3:.4}'.format( item[0], item[1], item[2].totalReturn, item[2].sharpie))
        return perfRes

    @staticmethod
    def GetPairTestPerf(pair: list, startDate: datetime, endDate: datetime, windowTest: int, retrieveMktData: bool):
        testcase = PairTrading(pair, 0, 1, windowTest )
        res, wts = testcase.backTest(startDate, endDate, retrieveMktData)
        perfTest = PerfMeasure(res[AbstractStrategy.dailyRet_label])
        perfTest.getPerfStats()
        return perfTest



# s = ["XLK", "XLV", "XLE", "XLY", "XLI", "XLRE", "XLP", "XLF", "XLC", "XLU", "XLB"]
# #s = ["XLV","XLRE"]
# windowTest = 63
# #PairTrading.PrepareData(s, datetime(2020,1,1),datetime(2022,12,31), windowTest)
# logging.info('Matrix Result 2020')
# trainRes = PairTrading.RunSymbolMatrixTest(s, datetime(2020,1,1),datetime(2020,12,31), windowTest, False)
# trainRes.sort(key = lambda x: x[2].totalReturn,  reverse= True)
# testSymbol = [(x[0], x[1]) for x in trainRes[:10]]
# logging.info('Matrix Result 2021')
# for pair in testSymbol:
#     testRes = PairTrading.GetPairTestPerf(pair, datetime(2021,1,1), datetime(2021,12,31), windowTest, False)
#     logging.info('Matrix Result: {0} - {1}, return: {2:.2%}, sharpie: {3:.4}'.format( pair[0], pair[1], testRes.totalReturn, testRes.sharpie))
# logging.info('Matrix Result 2022')
# for pair in testSymbol:
#     testRes = PairTrading.GetPairTestPerf(pair, datetime(2022,1,1), datetime(2022,12,31), windowTest, False)
#     logging.info('Matrix Result: {0} - {1}, return: {2:.2%}, sharpie: {3:.4}'.format( pair[0], pair[1], testRes.totalReturn, testRes.sharpie))



#PairTrading.RunSymbolMatrixTest(s, datetime(2021,1,1),datetime(2021,12,31), windowTest)
#PairTrading.RunSymbolMatrixTest(s, datetime(2022,1,1),datetime(2022,12,31), windowTest)



testcase = PairTrading(['mdy', 'spy'], 5, 1, 63, 4)
res, wts = testcase.backTest(datetime(2022,1,1), datetime(2023,12,31), True)
testcase.ShowPerformance(res)
#signal = testcase.EvalTradeSignal()
signal = testcase.lastTrade.daysSinceLastTrade == 1
zcore = res.loc[res.index[-1], PairTrading.zscore_lbl]
print("Signal: {}, ZScore: {}".format(signal,  zcore))


# examSymbols = [
#                 ('v', 'ma'), 
#                 ('mdy', 'voo'), 
#                 ('xlv', 'xlre'),
#                 ('xlv', 'xlc'),
#                 ('xly', 'xli')
#             ]
# for pair in examSymbols:
#     try:
#         t = PairTrading(list(pair), 0, 1, 63)
#         signal = t.EvalTradeSignal()
#         print("Signal: {}, Pair: {}, Price: ({}, {}), ZScore: {}, ".format(signal.HasTradeSignal, pair, 
#                 signal.status[str.upper(pair[0])], signal.status[str.upper(pair[1])],
#                 signal.status[PairTrading.zscore_lbl]))
#     except Exception as e :
#         print('Fail to process {}, error: {}'.format(pair, e))
#         logging.error(traceback.format_exc())

# s1, s2 = 'USO', 'DUG'
# johntest = MarketDataMgr.getEquityDataSingleField([s1, s2], MarketDataMgr.adjcls_lbl, datetime(2021,9,1), datetime(2022,9,1))

# isCoint = johansenCointTest(johntest)

# print(isCoint)

# res= coint_johansen(johntest, 0, 1)
# print(type(res.cvm))
# #print(coint(johntest[s1], johntest[s2]))
# output = pd.DataFrame([res.lr2,res.lr1],
#                           index=['max_eig_stat',"trace_stat"])
# print(output.T,'\n')
# print("Critical values(90%, 95%, 99%) of max_eig_stat\n",res.cvm,'\n')
# print("Critical values(90%, 95%, 99%) of trace_stat\n",res.cvt,'\n')