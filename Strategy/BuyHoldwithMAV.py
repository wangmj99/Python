from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt

"""
Long stock1 if above moving average, long stock2 if stock1 is below moving average
"""
class BuyHoldwithMovingAvg(Strategy):

    def __init__(self, stock1:str, stock2:str, movingWindow=50, cooldowndays = 0, leverage =1):
        self.stock1 =str.upper(stock1)
        self.stock2 = str.upper(stock2)
        self.window = movingWindow
        self.leverage = leverage
        self.cooldowndays = cooldowndays  #cooldowndays after previous trade, to avoid frequent trades
        self.daysSinceLastTrade = 0
        self.lastTradePrice = () #tuple to record last trade stock1 price and stock1 moving avg
        

    def backTest(self, startDate: datetime, endDate: datetime):
        """
        1. Get history data for stock1 and stock2
        2. rolling moving average for stock1
        3. generate position based on moving avg
        4. generate pnlSummary
        5. generate performance measure
        """
        
        df = retreiveEquityAdjCloseTable([self.stock1, self.stock2], startDate, endDate)
        rolling = df[self.stock1].rolling(self.window)
        mvg = rolling.mean().shift(1) 
        df['MVG'] = mvg
        #df['PreClose'] = df[self.stock1].shift(1)
        df = df.dropna()
        
        wts = pd.DataFrame(columns=[self.stock1, self.stock2])

        for index, row in df.iterrows():
            if len(self.lastTradePrice) >0  and self.daysSinceLastTrade <= self.cooldowndays: # still in cooldownday:
                self.daysSinceLastTrade +=1
                continue

            if row[self.stock1] >= row['MVG'] and (len(self.lastTradePrice) ==0 or self.lastTradePrice[0] < self.lastTradePrice[1]):
                wts.loc[index] = [1*self.leverage, 0]
            elif row[self.stock1] < row['MVG'] and (len(self.lastTradePrice) ==0 or self.lastTradePrice[0] >= self.lastTradePrice[1]):
                wts.loc[index] = [0, 1]
            self.daysSinceLastTrade = 1
            self.lastTradePrice=(row[self.stock1], row['MVG'])
        
        dailyRet= GetDailyPnlFromPriceAndWeightChg(df[[self.stock1, self.stock2]], wts).rename('dailyRet')
        df=pd.concat([df, dailyRet], axis = 1, join = 'inner')

        wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))                
        df.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        
        perf1 = PerfMeasure.getPerfStatsFromDailyPnl(df['dailyRet'])
        print(perf1.sharpie, perf1.mean)
        plotTwoYAxis([df['MVG'],df[self.stock1]], [perf1.statsTable['cumret']])

        perf2 = PerfMeasure.getPerfStatsFromDailyPnl(df[self.stock1].pct_change().fillna(0))
        print(perf2.sharpie, perf2.mean)

testcase = BuyHoldwithMovingAvg('spy', 'tlt', 120,20, 2)
testcase.backTest(datetime(2010,1,1), datetime(2020,12,31))



