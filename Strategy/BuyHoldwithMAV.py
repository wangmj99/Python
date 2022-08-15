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
        df['PreClose'] = df[self.stock1].shift(1)
        df = df.dropna()
        df['hold1']=0.0
        df['hold2']=0.0

        df['s1ret'] = df[self.stock1].pct_change().fillna(0)
        df['s2ret'] = df[self.stock2].pct_change().fillna(0)

        df['dailyRet'] = 0.0
        

        """
        1. if first row: set val count+1
        2. if <= cooldown:  copy previous row, count+1
        3. if >cooldown: 
            if val same as previous day count+1
            if val different, reset count
        """
        preRow = None
        for index, row in df.iterrows():
            if preRow is None:  # first Row
                self.setRowVal(row)
                self.daysSinceLastTrade =1
            else:
                if self.daysSinceLastTrade <= self.cooldowndays: # still in cooldownday
                    row['hold1'] = preRow['hold1']
                    row['hold2'] = preRow['hold2']
                    self.daysSinceLastTrade +=1
                else:               # not in cooldownday, check if value changed
                    self.setRowVal(row)
                    if row['hold1'] == preRow['hold1']: 
                        self.daysSinceLastTrade+=1
                    else: 
                        self.daysSinceLastTrade =1
            preRow = row           
            row['dailyRet'] = row['hold1']*row['s1ret'] + row['hold2']*row['s2ret'] 
            
      
        df.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        
        perf1 = PerfMeasure.getPerfStatsFromDailyPnl(df['dailyRet'])
        print(perf1.sharpie, perf1.mean)
        plotTwoYAxis([df['MVG'],df[self.stock1]], [perf1.statsTable['cumret']])


        perf2 = PerfMeasure.getPerfStatsFromDailyPnl(df['s1ret'])
        print(perf2.sharpie, perf2.mean)

    def setRowVal(self, row):
        if row['PreClose']- row['MVG']>=0:
            row['hold1'] = 1*self.leverage
            row['hold2'] = 0
        else: 
            row['hold1'] = 0
            row['hold2'] = 1

testcase = BuyHoldwithMovingAvg('spy', 'tlt', 50,20, 1)
testcase.backTest(datetime(2000,1,1), datetime(2022,12,31))



