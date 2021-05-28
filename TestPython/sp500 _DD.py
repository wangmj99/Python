import pandas as pd 
#import statsmodels.api as smf
import statsmodels.formula.api as smf
import numpy as np 
import matplotlib.pyplot as plt 

# reduce portfolio to 50% if  drawdown 5% within 30 days, reinvest after recover to 100%

class Holding:
  def __init__(self, shares, cash):
    self.shares = shares
    self.cash = cash

  def get_wealth(self, price):
    return self.shares*price + self.cash


sp500 = pd.read_csv('./data/indice/SP500.csv', index_col=0)
cashratio = 0.4
daysOfMonth = 21
drawdown = 0.12
popup = 0.01

aum = 10000.00

df2 = pd.DataFrame(index = sp500.index)
df2['close'] = sp500['Close']
df2['daily_return'] = df2['close']/df2['close'].shift(1)-1

df2['share']=np.NaN
df2['cash'] =np.NaN
df2['wealth'] = np.NaN
df2['wealthlochigh'] = np.NaN
df2['wealthloclow'] = np.NaN
df2['peak'] = np.NaN

df = df2.loc['2007-1-01':'2020-12-12']



df['share'][0] = float(aum)/df.iloc[0]['close']
df['cash'] [0] = 0
df['wealth'] [0]= aum
df['wealthlochigh'] [0]= aum
df['wealthloclow'] [0]= aum
df['peak'] [0]= aum

df['spy'] = aum/df['close'][0]*df['close']


def getlocalhigh(idx, df, days):
    start = 0
    start2 = 0
    end = idx
    if idx >days: 
        start = idx - days +1
        start2 = idx - days*2+1
    if idx>=len(df)-1:
        end = len(df)-1
    temp = df.iloc[start: end]['wealth']
    temp2 = df.iloc[start2: end]['wealth']
    
    return temp.max(), temp2.min()


#print(df.index.get_loc('1990-01-03'))
for idx in range(1, len(df)):
    localhigh, locallow  = getlocalhigh(idx, df, daysOfMonth)

    if df['wealth'][idx-1]<=df['peak'][idx-1]*(1-drawdown) and df['cash'][idx-1] < 0.1:
        val = df['wealth'][idx-1]*cashratio
        #df['cash'][idx] = val
        df.loc[df.index[idx], 'cash'] = val

        df.loc[df.index[idx], 'share']  = df['share'][idx-1] - df['cash'][idx]/df['close'][idx-1]
        

    
    elif df['wealth'][idx-1]>=df['peak'][idx-1] and df['cash'][idx-1] > 0.1:
        df.loc[df.index[idx], 'share'] = df['cash'][idx-1]/df['close'][idx-1] + df['share'][idx-1]
        df.loc[df.index[idx], 'cash']  = 0

    else:
        df.loc[df.index[idx], 'share'] =  df['share'][idx-1] 
        df.loc[df.index[idx], 'cash'] =  df['cash'][idx-1] 

    df.loc[df.index[idx], 'wealth'] = df['cash'][idx] + df['close'][idx]*df['share'][idx]
    df.loc[df.index[idx], 'wealthlochigh']  = localhigh
    df.loc[df.index[idx], 'wealthloclow'] = locallow
    df.loc[df.index[idx], 'peak'] = max (df['peak'][idx-1], df['wealth'][idx])

path_save = './data/DD.csv'
df.to_csv(path_save)

print(df.tail(30))
#print(df['close'][1])

df['wealth'].plot(color = 'red')
df['spy'].plot(color = 'black')
df['cash'].plot()
plt.show()
    