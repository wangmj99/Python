from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
from FinUtil import *
from MarketDataMgr import *
from BuyHoldRebalanceTemplate import * 


class PairTrading(BuyHoldRebalanceTemplate):
    spread_lbl, zscore_lbl, mean_lbl, std_lbl, beta_lbl = 'spread', 'rollingZ', 'Mean', 'Std', 'Beta'
    logging.basicConfig(filename="./logs/PairTrading.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')    

    def __init__(self, symbols: list, cooldowndays=0, leverage=1, window = 50):
        super().__init__(symbols, cooldowndays, leverage)
        self.window = window

    def BuildWeightsTable(self, mkd:pd.DataFrame, wts: pd.DataFrame):
        s1, s2 = self.symbols[0], self.symbols[1]

        mkd[PairTrading.zscore_lbl] = 0.0
        mkd[PairTrading.spread_lbl] = 0.0
        mkd[PairTrading.mean_lbl]= 0.0
        mkd[PairTrading.std_lbl] = 0.0
        mkd[PairTrading.beta_lbl]= 0.0

        #wts= pd.DataFrame(columns=[s1, s2])
        upThld, lowThld = 1.65, 0.5
        oldSignal = 0 # 1 long spread, -1 short spread, 0 no postion

        for t in range(self.window-1, len(mkd)):
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
            if oldSignal == 0:
                if zscore >= upThld:
                    wts.loc[idx] = [-1, 1]
                    oldSignal = -1
                    flag = True
                elif zscore <= -upThld:
                    wts.loc[idx] = [1, -1]
                    oldSignal = 1
                    flag = True
            elif oldSignal == 1:
                if zscore >=-lowThld:
                    wts.loc[idx] = [0,0]
                    oldSignal = 0
                    flag = True
            else:  # oldsignla = -1
                if zscore <= lowThld:
                    wts.loc[idx] = [0,0]
                    oldSignal = 0
                    flag = True

            if flag == True:
                actionstr = actionStr = 'Enter Trade' if wts.loc[idx, s1]!=0 else 'Exit Trade'
                logging.info('{0}, action: {1}'. format(self.CreateLogEntry(self.symbols, mkd, wts, idx), actionStr))
                
                logging.info('--------> zscore: {0}, mean: {1}, std: {2}'.format(
                    mkd.loc[idx][PairTrading.zscore_lbl], 
                    mkd.loc[idx][PairTrading.mean_lbl], 
                    mkd.loc[idx][PairTrading.std_lbl]))
                    

        wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))
        mkd.to_csv(MarketDataMgr.dataFilePath.format('tmp'))
        

    def ShowPerformance(self, res: pd.DataFrame, benchmark: str = None):
        perf1 = PerfMeasure(res[BuyHoldRebalanceTemplate.dailyRet_label])
        perf1.getPerfStats()
        logging.info('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}, KellyWeight: {:.2%}'.
        format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn, perf1.kellyWeight/2))
        plotTwoYAxis([res[PairTrading.spread_lbl]], [perf1.statsTable['cumret']])

        res[PairTrading.beta_lbl].plot()

        if benchmark != None:
            self.ShowBenchmarkPerformance(benchmark,res.index[0], res.index[-1])

testcase = PairTrading(['v', 'ma'], 0, 1, 63)
res = testcase.backTest(datetime(2022,1,1), datetime(2022,12,31))
testcase.ShowPerformance(res, 'Agg')

