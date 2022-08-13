from FinUtil import *
from MarketDataMgr import *
from datetime import datetime

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
        
        for index, row in df.iterrows():
            if row['PreClose']- row['MVG']>=0:
                row['hold1'] = 1*self.leverage
                row['hold2'] = 0
            else: 
                row['hold1'] = 0 
                row['hold2'] = 1
        
        df.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

testcase = BuyHoldwithMovingAvg('spy', 'tlt', 50)
testcase.backTest(datetime(2015,2,1), datetime(2016,12,31))



