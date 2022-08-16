from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging

"""
Long stock1 if above moving average, long stock2 if stock1 is below moving average
"""
class BuyHoldwithMovingAvg(Strategy):

    logging.basicConfig(filename="./logs/BuyHoldwithMovingAvg.log", level=logging.INFO,
                    format="%(asctime)s %(message)s", datefmt='%d-%b-%y %H:%M:%S')

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
        logging.info('---------------------------------------Start BackTest--------------------------------------')
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

            flag = False
            if row[self.stock1] >= row['MVG'] and (len(self.lastTradePrice) ==0 or self.lastTradePrice[0] < self.lastTradePrice[1]):
                wts.loc[index] = [1*self.leverage, 0]
                flag = True
            elif row[self.stock1] < row['MVG'] and (len(self.lastTradePrice) ==0 or self.lastTradePrice[0] >= self.lastTradePrice[1]):
                wts.loc[index] = [0, 1]
                flag = True
            
            if flag:
                wtsStr = '{}: {}, {}: {}'.format(self.stock1,wts.loc[index][self.stock1], self.stock2, wts.loc[index][self.stock2] )
                logging.info("Entry date: {0}, rebalance  {1} price: {2}, mvg: {3}, {4} price: {5}, wts: {6}".
                format(index.strftime('%m-%d-%Y'), self.stock1, round(row[self.stock1],2), round(row['MVG'],2), self.stock2, round(row[self.stock1],2), wtsStr))
                self.daysSinceLastTrade = 1
                self.lastTradePrice=(row[self.stock1], row['MVG'])
        
        dailyRet= GetDailyPnlFromPriceAndWeightChg(df[[self.stock1, self.stock2]], wts).rename('dailyRet')
        df=pd.concat([df, dailyRet], axis = 1, join = 'inner')

        wts.to_csv(MarketDataMgr.dataFilePath.format('tmp_wts'))                
        df.to_csv(MarketDataMgr.dataFilePath.format('tmp'))

        perf1 = PerfMeasure(df['dailyRet'])
        perf1.getPerfStatsFromDailyPnl()
        logging.info('********************** Strategy sharpie(yearly): {}, mean: {}, std: {}, totalReturn: {:.2%}'.format(perf1.sharpie, perf1.mean, perf1.std, perf1.totalReturn))
        plotTwoYAxis([df['MVG'],df[self.stock1]], [perf1.statsTable['cumret']])

        perf2 = PerfMeasure(df[self.stock1].pct_change().fillna(0))
        perf2.getPerfStatsFromDailyPnl()
        logging.info('********************** Benchmark sharpie(yearly): {}, mean: {}, std: {}, totalReturn: {:.2%}'.format(perf2.sharpie, perf2.mean, perf2.std, perf2.totalReturn))
testcase = BuyHoldwithMovingAvg('spy', 'tlt', 50,20, 2)
testcase.backTest(datetime(2022,1,1), datetime(2022,12,31))



