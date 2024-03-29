from datetime import datetime
from socket import INADDR_MAX_LOCAL_GROUP
from typing import Tuple
import pandas as pd
import math
from abc import ABC,abstractmethod
import os.path
from MarketDataMgr import *
import matplotlib.pyplot as plt
from statsmodels.tsa.vector_ar.vecm import coint_johansen 
import numpy as np
import statsmodels.formula.api as smf

class PerfMeasure:
    def __init__(self,dailyPnl:pd.Series) -> None:
        self.dailyPnl = dailyPnl


    #@staticmethod
    def getPerfStats(self, period = 252):
        self.mean = self.dailyPnl.mean()
        self.std = self.dailyPnl.std()
        self.sharpie = math.sqrt(period)*self.mean/self.std
        self.kellyWeight = self.mean/(self.std**2)

        df = pd.DataFrame({'pnl': self.dailyPnl})
        df['cumret'] = (1+df['pnl']).cumprod()-1

        df['cummax'] = df['cumret'].cummax()
        df['drawdown'] = (df['cumret'] - df['cummax'])/(1+df['cummax'])
        vallist  = [ ]
        for v in df['drawdown'].values:
            if len(vallist) == 0: vallist.append(0)
            elif v == 0:
                vallist.append(0)
            else:
                vallist.append(vallist[-1]+1)
        drawdays = pd.Series(vallist)
        drawdays.index = df['drawdown'].index
        df['drawdowndays'] = drawdays
        self.statsTable = df

        self.totalReturn = df['cumret'][-1]

        df.to_csv('./data/tmpPD.csv')

class Strategy(ABC):
    #@abstractmethod
    #Abstract method  stock price time series and generate long/short position
    def generateSingleEquityPosition(self, df: pd.Series) -> pd.Series:
        pass
    
    #@abstractmethod
    #Abstract method take list of stock price time series and generate position for each stock
    #return dataframe for each stock with position of time series
    def generateMultipleEquityPosition(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

def getDailyPnlFromPriceAndPosition(prices: pd.Series, positions:pd.Series) -> pd.Series:
    ret = prices.pct_change()
    ret = ret.fillna(0)

    pnl = pd.Series([x*y for x,y  in zip(ret,positions)])
    pnl.index = prices.index
    return pnl

def getDailyPnlFromPrice(prices: pd.Series)->pd.Series:
    res = prices.pct_change().fillna(0)
    return res

def getSeriesIntersectByIndex(s1: pd.Series, s2: pd.Series) -> tuple():
    ixs = s1.index.intersection(s2.index)
    if len(ixs) == 0: return None
    else:
        return (s1[ixs], s2[ixs])

# input list of price series represent multiple stock prices, share weights for each stock weight in porfolio
def getPortfolioDailyNAVByPriceAndFixedPosition(prices: list, weights: list)->pd.Series:
    if len(prices)!=len(weights): return None

    nav = []
    count = len(prices[0])
    for i in range(count):
        currVal = 0
        for j in range(len(weights)):
            currVal += prices[j].iloc[i]*weights[j]
        nav.append(currVal)
    res = pd.Series(nav)
    res.index = prices[0].index
    return res

# input list of price series represent multiple stock prices, share weights series for each stock weight in porfolio
# both prices and weights have the same datetime index
def getPortfolioDailyNAVByPriceAndDynPosition(prices: list, weights: list)->pd.Series:
    nav = []
    index = prices[0].index
    for idx in index:
        val = 0
        for j in range(len(prices)):
            val+= prices[j][idx]*weights[j][idx]
        nav.append(val)
    
    res = pd.Series(nav)
    res.index = index
    return res
    
# input list of price series represent multiple stock prices, share weights for each stock weight in porfolio
def getPortfolioDailyPnlByPriceAndFixedPosition(prices: list, weights: list)->pd.Series:
    if len(prices)!=len(weights): return None

    nav = getPortfolioDailyNAVByPriceAndFixedPosition(prices, weights)
    res = getDailyPnlFromPrice(nav)

    return res

#Take a list of equity history data as csv files and output adjust close in dataframe format
def getEquityAdjCloseTable(symbols: list, startDate: datetime, endDate:datetime, innerjoin = True )->pd.DataFrame:
    return MarketDataMgr.getEquityDataSingleField(list, MarketDataMgr.adjcls_lbl, startDate, endDate, innerjoin)

def genereateRollingZscore(srs: pd.Series, window: int):
    r = srs.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (srs-m)/s
    return z

#Get daily return from cummulative return
def getDailyPnlFromCumReturn(cumRet: pd.Series)->pd.Series:
    dailyRet = []
    for i in range(len(cumRet)):
        if i == 0:
            dailyRet.append(cumRet.iloc[i])
            continue
        val = (cumRet.iloc[i]-cumRet.iloc[i-1])/(1+cumRet.iloc[i-1])
        dailyRet.append(val)
    res = pd.Series(dailyRet)
    res.index = cumRet.index
    return res
        
def plotTwoYAxis(group1:list, group2:list):
    fig, ax = plt.subplots()
    for i in range(len(group1)):
        ser = group1[i]
        if i == 0:
            ax.plot(ser, color = 'pink')
        else:
            ax.plot(ser)
    ax.tick_params(axis='y', labelcolor='red')

    ax2 = ax.twinx()
    for i in range(len(group2)):
        ser = group2[i]
        if i == 0:
            ax2.plot(ser, color = 'green')
        else : 
            ax2.plot(ser)
    #ax2.set_yscale('log')
    ax2.tick_params(axis='y', labelcolor='green')

    plt.show()

# input list of price series represent multiple stock prices and  portfolio weights (pct, add to 100%) series for each stock.
# weight series only contain the weights update for each buy/sell transactions.
# eg. portfolio weights change at day1 and day3, weithgs series should be  day1: 20%, 0%, 80% , day3: 50%, 10%,40%, there is no entry for day2
def GetDailyPnlFromPriceAndWeightChg(prices: pd.DataFrame, wgts: pd.DataFrame, startDate: datetime, endDate: datetime):

    #wgts['total'] = wgts.sum(axis=1)
    #lm = lambda x: 1 if abs(1- x['total'])<=0.001 else (0 if abs(x['total'])<=0.001 else -1)

    lastUpdate= {} #dictionary contains price and weight at last update
    cumRetBeforeLastUpdate = 0
    symbols = list(prices.columns)

    firstIdx = wgts.index[0]
    prices = prices[firstIdx: ]

    pnl = []
    for index, row in prices.iterrows():
        if index > endDate: 
            break
        tmpPnl = 0
        if index in wgts.index:
            #find update
            if len(pnl) == 0: #first row     
                for symbol in symbols:
                    lastUpdate[symbol] = (row[symbol], wgts[symbol][index])
                cumRetBeforeLastUpdate = 0
                pnl.append(0)
            else :
                for symbol in symbols:
                    w = lastUpdate[symbol][1]
                    p = lastUpdate[symbol][0]
                    tmpPnl += w*(row[symbol]/p-1)
                
                currRet = (1+cumRetBeforeLastUpdate)*(1+tmpPnl)-1
                pnl.append(currRet)

                for symbol in symbols:
                    lastUpdate[symbol] = (row[symbol], wgts[symbol][index])
                cumRetBeforeLastUpdate = currRet
                
        else:
            for symbol in symbols:
                    w = lastUpdate[symbol][1]
                    p = lastUpdate[symbol][0]
                    tmpPnl += w*(row[symbol]/p-1)
            currRet = (1+cumRetBeforeLastUpdate)*(1+tmpPnl)-1
            pnl.append(currRet)
    cumRet = pd.Series(pnl).rename('cumRet')
    idxLoc = prices.index.get_loc(firstIdx)
    cumRet.index = prices.index[idxLoc: idxLoc + len(pnl)]
    res = getDailyPnlFromCumReturn(cumRet)
    """
    tmpPD = pd.concat([prices, cumRet], axis = 1, join = 'inner')
    tmpPD = pd.concat([tmpPD, res], axis = 1, join = 'inner')
    tmpPD.to_csv('./data/tmpPD.csv')
    """

    return res
                
def joh_output(res):
    output = pd.DataFrame([res.lr2,res.lr1],
                          index=['max_eig_stat',"trace_stat"])
    print(output.T,'\n')
    print("Critical values(90%, 95%, 99%) of max_eig_stat\n",res.cvm,'\n')
    print("Critical values(90%, 95%, 99%) of trace_stat\n",res.cvt,'\n')


#input 2 series and confidence level to check if they are cointegrated, return True or False
def johansenCointTest(df: pd.DataFrame, confidenceLvl = 90):
    result = coint_johansen(df, 0, 1)
    confidence_level_cols = {
        90: 0,
        95: 1,
        99: 2
    }
    confidence_level_col = confidence_level_cols[confidenceLvl]
    
    trace_crit_value = result.cvt[:, confidence_level_col]
    eigen_crit_value = result.cvm[:, confidence_level_col]
    
    # The trace statistic and maximum eigenvalue statistic are stored in lr1 and lr2;
    # see if they exceeded the confidence threshold
    res = np.all(result.lr1 >= trace_crit_value) and np.all(result.lr2 >= eigen_crit_value)
    return res

def CalcHalfHoldingPeriod(spread: pd.Series):
    prv = spread.shift(1)
    delta = spread - prv

    prv = prv.dropna()
    delta = delta.dropna()

    mean = prv.mean()
    prv = prv- mean

    frame = {'delta': delta, 'prv': prv}
    df =pd.DataFrame(frame)

    f = '{}~{}'.format('delta', 'prv')
    lm = smf.ols(formula=f, data=df).fit()

    theate = lm.params[1]

    res=  -np.log(2)/theate

    return res


# idx = pd.date_range('1/1/2021', periods=10, freq='D')
# s1 = pd.Series([x for x in range(1,11)])
# s1.index = idx

# holding = CalcHalfHoldingPeriod(s1)


        
# price = {'SPY': [350.209991,354.670013,355.869995,346.130005,336.709991,337.549988,341.820007,335.820007,337.48999,341.119995], 
#         'TLT': [161.759995,163.509995,165.75,164.410004,164.369995,163.940002,162.460007,164.309998,164.789993,164.169998]}

# wts = {'SPY':[1.5,0.5], 'TLT':[-0.5, 0.5], 'Date':[datetime(2021,9,1), datetime(2021, 9,7)]}

# idx_p = pd.date_range('9/1/2021', periods=10, freq='D')    

# df1 = pd.DataFrame(price)
# df1.index = idx_p
# df2 = pd.DataFrame(wts)
# df2.set_index('Date', inplace=True)

# GetDailyPnlFromPriceAndWeightChg(df1, df2)