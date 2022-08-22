from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math 
import statsmodels.formula.api as smf
from FinUtil import *
from MarketDataMgr import *

def calcHedgeDrawDown():
    startDate = datetime.strptime('01/01/2000', '%m/%d/%Y')
    endDate  = datetime.strptime('09/01/2022', '%m/%d/%Y')
    s1,s2 = 'V', 'MA'
    #MarketDataMgr.retrieveHistoryData([s1, s2], startDate, endDate)

    df = retreiveEquityAdjCloseTable([s1, s2], startDate, endDate)
    s1df= df[s1].pct_change()
    s2df= df[s2].pct_change()
    hedge = (s1df.dropna()-s2df.dropna())
    
    perf= PerfMeasure.getPerfStats(hedge)
    print(perf.sharpie)
    perf.statsTable['cumsum'].plot()
    plt.show()

def pairTrading(s1:str, s2:str, startDate: datetime, endDate:datetime):
    s1, s2 = str.upper(s1), str.upper(s2)
    df = retreiveEquityAdjCloseTable([s1, s2], startDate, endDate)

    mid = int(len(df)/2)
    train = df.iloc[:mid]
    test = df.iloc[mid:]

    f = '{}~{}'.format(s1, s2)
    lm = smf.ols(formula=f, data=train).fit()
    print(lm.summary())

    train_nav = getPortfolioDailyNAVByPriceAndFixedPosition([train[s1], train[s2]], [1, -lm.params[1]])
    train_zscore = (train_nav - train_nav.mean())/train_nav.std()
    train_posSeries = CreatePairTradingPositionByZscore(train_nav)
    train_pnl = getDailyPnlFromPriceAndPosition(train_nav, train_posSeries)
    train_perf = PerfMeasure.getPerfStats(train_pnl)
    train_pnldf = train_perf.statsTable

    test_nav = getPortfolioDailyNAVByPriceAndFixedPosition([test[s1], test[s2]], [1, -lm.params[1]])
    test_zscore = (test_nav - test_nav.mean())/test_nav.std()
    test_posSeries = CreatePairTradingPositionByZscore(test_nav)
    test_pnl = getDailyPnlFromPriceAndPosition(test_nav, test_posSeries)
    test_perf = PerfMeasure.getPerfStats(test_pnl)
    test_pnldf = test_perf.statsTable

    print('train: sharpie:{}, mean: {}, std: {}'.format(train_perf.sharpie, train_perf.mean, train_perf.std))
    print('test : sharpie:{}, mean: {}, std: {}'.format(test_perf.sharpie, test_perf.mean, test_perf.std))

    #path_save = './data/PairTrading.csv'
    #savepd.to_csv(path_save)
    test_pnldf['cumsum'].plot()
    test_zscore.plot()
    plt.show()
    #print(df.describe())

def CreatePairTradingPositionByZscore(spread):
    pos = []
    zscore = (spread - spread.mean())/spread.std()
    zinit, zexit = 0.75, 0.5
    for zval in zscore:
        if len(pos) == 0:
            if zval>=zinit:
                pos.append(-1) # short spread
            elif zval <=-zinit:
                pos.append(1) # long spread
            else:
                pos.append(0)
        else:
            if pos[-1] == 0:
                if zval>=zinit:
                    pos.append(-1) # short spread
                elif zval <=-zinit:
                    pos.append(1) # long spread
                else:
                    pos.append(0)
            elif pos[-1] == 1:
                if abs(zval) <= zexit or zval > zinit:
                    pos.append(0) # exit position
                else:
                    pos.append(1)
            elif pos[-1] == -1:
                if abs(zval) <= zexit or zval <- zinit:
                    pos.append(0) # exit position
                else:
                    pos.append(-1)               
    posSeries = pd.Series(pos, index=zscore.index)
    posSeries = posSeries.shift(1).fillna(0)
    return posSeries


def pairTrading2(s1:str, s2:str, startDate: datetime, endDate:datetime, window = 21*3):
    s1, s2 = str.upper(s1), str.upper(s2)
    dataSet = retreiveEquityAdjCloseTable([s1, s2], startDate, endDate)

    dataSet['rollingZ'] = 0.0
    dataSet['spread'] = 0.0

    wts= pd.DataFrame(columns=[s1, s2])
    upThld, lowThld = 1.65, 0.5
    oldSignal = 0 # 1 long spread, -1 short spread, 0 no postion

    for t in range(window-1, len(dataSet)):
        tmpdf = dataSet.iloc[t-window+1:t+1]
        
        f = '{}~{}'.format(s1, s2)
        lm = smf.ols(formula=f, data=tmpdf).fit()
        
        tmpSprd = tmpdf[s1]-tmpdf[s2]*lm.params[1]
        zscore = (tmpSprd[-1] - tmpSprd.mean())/tmpSprd.std()

        idx = dataSet.index.values[t]
        dataSet.loc[idx, 'rollingZ'] = zscore
        dataSet.loc[idx, 'spread'] = tmpSprd[-1]
        

        if oldSignal == 0:
            if zscore >= upThld:
                wts.loc[idx] = [-1, 1]
                oldSignal = -1
            elif zscore <= -upThld:
                wts.loc[idx] = [1, -1]
                oldSignal = 1
        elif oldSignal == 1:
            if zscore >=-lowThld:
                wts.loc[idx] = [0,0]
                oldSignal = 0
        else:  # oldsignla = -1
            if zscore <= lowThld:
                wts.loc[idx] = [0,0]
                oldSignal = 0

    wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))
    dataSet.to_csv(MarketDataMgr.dataFilePath.format('tmp'))
    
    dailyRet= GetDailyPnlFromPriceAndWeightChg(dataSet[[s1, s2]], wts).rename('dailyRet')
    perf1 = PerfMeasure(dailyRet)
    perf1.getPerfStats()
    print('********************** Strategy sharpie(yearly): {:.4}, mean(daily): {:.4}, std(daily): {:.4}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
    plotTwoYAxis([dataSet['spread']], [perf1.statsTable['cumret']])






pairTrading2('mdy', 'spy', datetime(2022,3,26), datetime(2022,12,31))
#calcHedgeDrawDown()


