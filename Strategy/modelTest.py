import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math 
import statsmodels.formula.api as smf
from FinUtil import *




def calcHedgeDrawDown():
    df = generateEquityDataFrame(['MDY', 'iwm'])
    ms= df['MDY'].pct_change()
    iwm= df['IWM'].pct_change()
    hedge = (ms.dropna()-iwm.dropna())

    res = getPnlSummary(hedge)
    
    perf= PerfMeasure.getPerf(hedge)
    print(perf.sharpie)
    print(res)
    res['cumsum'].plot()
    plt.show()

def pairTrading(s1, s2):
    s1, s2 = str.upper(s1), str.upper(s2)
    df = generateEquityAdjCloseTable([s1, s2])

    mid = int(len(df)/2)
    train = df.iloc[:mid]
    test = df.iloc[mid:]

    f = '{}~{}'.format(s1, s2)
    lm = smf.ols(formula=f, data=train).fit()
    print(lm.summary())

    train_nav = getPortfolioDailyNAVByPriceAndWeight([train[s1], train[s2]], [1, -lm.params[1]])
    train_zscore = (train_nav - train_nav.mean())/train_nav.std()
    train_posSeries = CreatePairTradingPositionByZscore(train_nav)
    train_pnl = getPnlFromPriceAndPosition(train_nav, train_posSeries)
    train_perf = PerfMeasure.getPerf(train_pnl)
    train_pnldf = getPnlSummary(train_pnl)

    test_nav = getPortfolioDailyNAVByPriceAndWeight([test[s1], test[s2]], [1, -lm.params[1]])
    test_zscore = (test_nav - test_nav.mean())/test_nav.std()
    test_posSeries = CreatePairTradingPositionByZscore(test_nav)
    test_pnl = getPnlFromPriceAndPosition(test_nav, test_posSeries)
    test_perf = PerfMeasure.getPerf(test_pnl)
    test_pnldf = getPnlSummary(test_pnl)

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


pairTrading('MDY', 'IWM')
#calcHedgeDrawDown()


"""
TODO
1. input 2 tickers, output pnl summary for both train and test set

"""