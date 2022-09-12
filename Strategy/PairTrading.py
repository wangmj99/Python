from datetime import date
from signal import SIGABRT
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
from FinUtil import *
from MarketDataMgr import *
from BuyHoldRebalanceTemplate import * 
import traceback
from statsmodels.tsa.vector_ar.vecm import coint_johansen 
from statsmodels.tsa.stattools import coint 


class PairTrading(BuyHoldRebalanceTemplate):
    spread_lbl, zscore_lbl, mean_lbl, std_lbl, beta_lbl = 'spread', 'rollingZ', 'Mean', 'Std', 'Beta'
    logging.basicConfig(filename="./logs/PairTrading.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    

    def __init__(self, symbols: list, cooldowndays=0, leverage=1, window = 50):
        super().__init__(symbols, cooldowndays, leverage)
        self.window = window
        self.warmupDays = window

    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame,startDate: datetime, endDate: datetime):
        s1, s2 = self.symbols[0], self.symbols[1]

        mkd[PairTrading.zscore_lbl] = 0.0
        mkd[PairTrading.spread_lbl] = 0.0
        mkd[PairTrading.mean_lbl]= 0.0
        mkd[PairTrading.std_lbl] = 0.0
        mkd[PairTrading.beta_lbl]= 0.0
        
        #wts= pd.DataFrame(columns=[s1, s2])
        upThld, lowThld = 1.65, 0.5
        tradeSignal = 'Signal'
        self.lastTrade.transTable = {tradeSignal : 0} # 1 long spread, -1 short spread, 0 no postion

        #get the startdate index in the dataframe
        startIdx = mkd.index.get_loc(startDate, method='bfill') 

        #mark the start position
        wts.loc[mkd.index[startIdx]] = [0,0]

        #for t in range(self.window-1, len(mkd)):
        for t in range(startIdx, len(mkd)):
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
            
            flag = False
            if self.lastTrade.transTable[tradeSignal] == 0:
                if zscore >= upThld:
                    wts.loc[idx] = [-1, 1]
                    self.lastTrade.transTable[tradeSignal] = -1
                    flag = True
                elif zscore <= -upThld:
                    wts.loc[idx] = [1, -1]
                    self.lastTrade.transTable[tradeSignal] = 1
                    flag = True
            elif self.lastTrade.transTable[tradeSignal] == 1:
                if zscore >=-lowThld:
                    wts.loc[idx] = [0,0]
                    self.lastTrade.transTable[tradeSignal] = 0
                    flag = True
            else:  # tradesignal = -1
                if zscore <= lowThld:
                    wts.loc[idx] = [0,0]
                    self.lastTrade.transTable[tradeSignal] = 0
                    flag = True

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
        

    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[BuyHoldRebalanceTemplate.dailyRet_label])
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
        res, wts = self.backTest(datetime(2021,1,1), endDate)
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

testcase = PairTrading(['spyd', 'spyg'], 0, 1, 63)
res, wts = testcase.backTest(datetime(2021,1,1), datetime(2022,12,31))
testcase.ShowPerformance(res, 'Agg')
signal = testcase.EvalTradeSignal()
print("Signal: {}, ZScore: {}".format(signal.HasTradeSignal,  signal.status[PairTrading.zscore_lbl]))


# examSymbols = [
#                 ('v', 'ma'), 
#                 ('mdy', 'spy'), 
#                 ('gdx', 'gld'), 
#                 ('pep', 'ko')
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



