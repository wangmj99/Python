import pandas as  pd 
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np 

ms = pd.read_csv('./data/MSFT.csv', index_col=0)

print(ms.describe())

#print(ms.loc['2020-01-01':'2020-01-31', :].tail())

#ms.loc['2020-01-01':'2020-01-31', 'Close'].plot()
#ms.loc['2020-02-01':'2020-02-30', 'Close'].plot()
#ms['Close'].plot()
#plt.show()


ms['PriceDiff'] = ms['Close'].shift(-1) - ms['Close']
ms['Return'] = ms['PriceDiff']/ms['Close']

ms['Direction'] = [1 if ms.loc[ei, 'Return']>0 else -1 for ei in ms.index]
ms['Fast'] = ms['Close'].rolling(20).mean()
ms['Slow'] = ms['Close'].rolling(50).mean()
ms=ms.dropna()



ms['Hold'] = [1 if ms.loc[ei, 'Fast']>ms.loc[ei, 'Slow'] else 0 for ei in ms.index]


ms['Profit'] = [ms.loc[ei,'PriceDiff'] if ms.loc[ei, 'Hold']==1 else 0 for ei in ms.index]



ms['Wealth']= ms['Profit'].cumsum()

#ms['Wealth'].plot()
#plt.axhline(y=0, color = 'red')


print(ms['Wealth'].mean(), ms['Wealth'].std(ddof=1))



z = (ms['Return'] -ms['Return'].mean())/ms['Return'].std(ddof=1)

#stats.probplot(z, dist='norm', plot=plt)

plt.show()
