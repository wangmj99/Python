import pandas as pd
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

class DateRange(Enum):
    Daily = 'D'
    Monthly = 'M'
    Quarterly = 'Q'
    Yearly = 'Y'
    

class MktDataManager:
    file_path = "./data/{}.csv"
    def readCSVData(self, ticker: str ) -> pd.DataFrame:
        filename = MktDataManager.file_path.format(ticker)
        df = pd.read_csv(filename, index_col = 0)      
        df.columns = map(lambda col: col.strip().lower(), df.columns)
        df.index = pd.to_datetime(df.index)
        df["dailyReturn"] = df['adj close'].pct_change()
        df = df.dropna()
        return df
        

    def calcReturnByDateRange(self, s:pd.Series, dr:DateRange) -> pd.Series:
        last_day  = s.resample(dr.value).agg(lambda x: x[-1])
        return last_day.pct_change()

    def calcMovingAvg(self, s:pd.Series, days: int) ->pd.Series:
        mv = s.rolling(days).mean()
        return mv

dm = MktDataManager()
df = dm.readCSVData('iwm')
ts= dm.calcReturnByDateRange(df['adj close'], DateRange.Monthly)
mv50 = dm.calcMovingAvg(df['adj close'],50)['2007-01-01':]
mv200 = dm.calcMovingAvg(df['adj close'],200)

diff = df['adj close']/mv50 -1
zscores = (diff-diff.mean())/diff.std()
zscoresGT2 = zscores[zscores<(-2)]

print(diff.mean(), diff.std())
#mv50.plot()
#mv200.plot()
zscores['2008-01-01':'2010-12-31'].plot()
#(df['dailyReturn']['2015-01-01':]*100).plot()
plt.show()

print(zscoresGT2)