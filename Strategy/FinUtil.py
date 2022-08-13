from datetime import datetime
from socket import INADDR_MAX_LOCAL_GROUP
from typing import Tuple
import pandas as pd
import math
from abc import ABC,abstractmethod
import os.path
from MarketDataMgr import *

class PerfMeasure:
    
    @staticmethod
    def getPerf(dailyPnl, period = 252):
        perf = PerfMeasure()
        perf.mean = dailyPnl.mean()
        perf.std = dailyPnl.std()
        perf.sharpie = math.sqrt(period)*perf.mean/perf.std
        return perf


 
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

def getPnlFromPriceAndPosition(prices: pd.Series, positions:pd.Series) -> pd.Series:
    ret = prices.pct_change()
    ret = ret.fillna(0)

    pnl = pd.Series([x*y for x,y  in zip(ret,positions)])
    pnl.index = prices.index
    return pnl

def getDailyPnl(prices: pd.Series)->pd.Series:
    res = prices.pct_change().fillna(0)
    return res

#get cummulative return, max and max drawdown from daily return
def getPnlSummary(pnl: pd.Series) -> pd.DataFrame:

    df = pd.DataFrame({'pnl': pnl})
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
    return df

def getSeriesIntersectByIndex(s1: pd.Series, s2: pd.Series) -> tuple():
    ixs = s1.index.intersection(s2.index)
    if len(ixs) == 0: return None
    else:
        return (s1[ixs], s2[ixs])

# input list of price series represent multiple stock prices, share weights for each stock weight in porfolio
def getPortfolioDailyNAVByPriceAndFixedWeight(prices: list, weights: list)->pd.Series:
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
def getPortfolioDailyNAVByPriceAndDynWeight(prices: list, weights: list)->pd.Series:
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
def getPortfolioDailyPnlByPriceAndFixedWeight(prices: list, weights: list)->pd.Series:
    if len(prices)!=len(weights): return None

    nav = getPortfolioDailyNAVByPriceAndFixedWeight(prices, weights)
    res = getDailyPnl(nav)

    return res

#Take a list of equity history data as csv files and output adjust close in dataframe format
def retreiveEquityAdjCloseTable(symbols: list, startDate: datetime, endDate:datetime, innerjoin = True )->pd.DataFrame:
    path = MarketDataMgr.dataFilePath
    closePriceLabel = 'Adj Close'
    res = None
    for symbol in symbols:
        md = MarketDataMgr.retrieveHistoryData([symbol], startDate, endDate)
        name= md[str.upper(symbol)]
        df = pd.read_csv(name, index_col=0)
        df.index = pd.to_datetime(df.index)
        df.sort_index(axis=0)
        temp = df[closePriceLabel].rename(str.upper(symbol))
        if res is None :
            res = pd.DataFrame(temp)
        else:
            if innerjoin:
                res = pd.concat([res, temp], axis = 1, join = 'inner')
            else :
                res = pd.concat([res, temp], axis = 1)
    return res

def genereateRollingZscore(srs: pd.Series, window: int):
    r = srs.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (srs-m)/s
    return z

#Get daily return from cummulative return
def getDailyRetFromCumRet(cumRet: pd.Series)->pd.Series:
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
        



s1 = pd.Series([0,0.1,0.08,0.09,0.12,0.10])
s2 = pd.Series([30,10,20,10,50])
w1 = pd.Series([1,1,0,0,1])
w2 = pd.Series([0,0,1,1,0])

print(getDailyRetFromCumRet(s1))
