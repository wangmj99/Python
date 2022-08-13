from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt

"""
Long stock1 if above moving average, long stock2 if stock1 is below moving average
"""
class BuyHoldwithMovingAvg(Strategy):

    def __init__(self, stock1:str, stock2:str, movingWindow=50, leverage =1):
        self.stock1 =str.upper(stock1)
        self.stock2 = str.upper(stock2)
        self.window = movingWindow
        self.leverage = leverage
        

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
        
        for index, row in df.iterrows():
            if row['PreClose']- row['MVG']>=0:
                row['hold1'] = 1*self.leverage
                row['hold2'] = 0
            else: 
                row['hold1'] = 0 
                row['hold2'] = 1
            row['dailyRet'] = row['hold1']*row['s1ret'] + row['hold2']*row['s2ret'] 
            
      
        df.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        perf1 = getPnlSummary(df['dailyRet'])
        perf1['cumsum'].plot()
        
        perf2 = getPnlSummary(df['s1ret'])
        perf2['cumsum'].plot()

        plt.show()
        perf = PerfMeasure.getPerf(df['dailyRet'])
        print(perf.sharpie, perf.mean)
        perf2 = PerfMeasure.getPerf(df['s1ret'])
        print(perf2.sharpie, perf2.mean)


testcase = BuyHoldwithMovingAvg('spy', 'tlt', 120, 2)
testcase.backTest(datetime(2012,2,1), datetime(2016,12,31))



