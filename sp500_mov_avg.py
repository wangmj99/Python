import pandas as pd
import matplotlib.pyplot as plt 
import math


sp500 = pd.read_csv('./data/indice/SP500.csv', index_col=0)

sp500['Price1'] =sp500['Close'].shift(-1)

sp500['mvAvg20'] = sp500['Close'].rolling(20).mean()
sp500['mvAvg50'] = sp500['Close'].rolling(50).mean()
sp500['Hold'] = [1 if sp500['mvAvg20'][idx]>sp500['mvAvg50'][idx] else 0 for idx in sp500.index]
sp500['PnL'] = [sp500['Price1'][idx] - sp500['Close'][idx] if sp500['Hold'][idx]>0 else 0 for idx in sp500.index ]
sp500['PnLPct'] = sp500['PnL']/sp500['Close']
sp500['TotalReturn'] = sp500['PnL'].cumsum()
sp500['TotalReturnPct'] = sp500['TotalReturn']/sp500['Close'][0]-1
sp500['SpyPnL'] = sp500['Price1'] - sp500['Close']
sp500['SpyPnLPct'] = sp500['Price1'] / sp500['Close']-1
sp500['SpyTotalReturn'] = sp500['SpyPnL'].cumsum()
sp500['SpyTotalReturnPct'] = sp500['SpyTotalReturn']/sp500['Close'][0]-1
sp500.dropna(inplace= True)

print(sp500.tail())

#path_save = './data/sp500MVAvg.csv'
#sp500.to_csv(path_save)

print(sp500['PnLPct'].mean()*250)
print(sp500['PnLPct'].std(ddof=1)*math.sqrt(250)) 

print(sp500['SpyPnLPct'].mean()*250)
print(sp500['SpyPnLPct'].std(ddof=1)*math.sqrt(250)) 

sp500['TotalReturn'].plot(color = 'green')
sp500['SpyTotalReturn'].plot(color = 'red')
plt.show()