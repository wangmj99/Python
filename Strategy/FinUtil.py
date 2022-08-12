from typing import Tuple
import pandas as pd
import math
from abc import ABC,abstractmethod

class PerfMeasure:
    
    @staticmethod
    def getPerf(dailyPnl, period = 252):
        perf = PerfMeasure()
        perf.mean = dailyPnl.mean()
        perf.std = dailyPnl.std()
        perf.sharpie = math.sqrt(period)*perf.mean/perf.std
        return perf


 
class Strategy(ABC):
    @abstractmethod
    #Abstract method  stock price time series and generate long/short position
    def generateSingleEquityPosition(self, df: pd.Series) -> pd.Series:
        pass
    
    @abstractmethod
    #Abstract method take list of stock price time series and generate position for each stock
    #return dataframe for each stock with position of time series
    def generateFullPosition(self, df: pd.DataFrame) -> pd.DataFrame:
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

#get cummulative return, max and max drawdown
def getPnlSummary(pnl: pd.Series) -> pd.DataFrame:

    df = pd.DataFrame({'pnl': pnl})
    df['cumsum'] = (1+df['pnl']).cumprod()-1

    df['cummax'] = df['cumsum'].cummax()
    df['drawdown'] = (df['cumsum'] - df['cummax'])/(1+df['cummax'])
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
def getPortfolioDailyNAVByPriceAndWeight(prices: list, weights: list)->pd.Series:
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


    
# input list of price series represent multiple stock prices, share weights for each stock weight in porfolio
def getPortfolioDailyPnlByPriceAndWeight(prices: list, weights: list)->pd.Series:
    if len(prices)!=len(weights): return None

    nav = getPortfolioDailyNAVByPriceAndWeight(prices, weights)
    res = getDailyPnl(nav)

    """ 
    pnl = [0]
    count = len(prices[0])
    for i in range(1, count):
        preVal, currVal = 0, 0
        for j in range(len(weights)):
            currVal += prices[j][i]*weights[j]
            preVal += prices[j][i-1]*weights[j]
        pval = currVal/preVal -1
        pnl.append(pval)
    res = pd.Series(pnl)
    res.index = prices[0].index 
    """
    return res

#Take a list of equity history data as csv files and output adjust close in dataframe format
def generateEquityAdjCloseTable(symbols: list, innerjoin = True )->pd.DataFrame:
    path = './data/{}.csv'
    closePriceLabel = 'Adj Close'
    res = None
    for symbol in symbols:
        name= path.format(symbol)
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

