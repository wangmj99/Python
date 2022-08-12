from numpy.lib.polynomial import polyval
import pandas as  pd 
import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
import scipy.stats as stats
import numpy as np 
from scipy.stats import norm 

ms = pd.read_csv('./data/MSFT.csv', index_col=0)

print(ms.head())
print(ms.describe())


#print(ms.loc['2020-01-01':'2020-01-31', 1:].tail())

#ms.loc['2020-01-01':'2020-01-31', 'Close'].plot()
#ms.loc['2020-02-01':'2020-02-30', 'Close'].plot()
#ms.loc[:,'Close'].plot()
#plt.show()


ms['PriceDiff'] = ms['Open'].shift(-1) - ms['Close']

ms['Return'] = ms['PriceDiff']/ms['Close']

ms['Direction'] = [1 if ms.loc[ei, 'Return']>0 else -1 for ei in ms.index]
ms['Fast'] = ms['Close'].rolling(20).mean()
ms['Slow'] = ms['Close'].rolling(50).mean()
ms=ms.dropna()

ms['Hold'] = [1 if ms.loc[ei, 'Fast']>ms.loc[ei, 'Slow'] else 0 for ei in ms.index]


ms['Profit'] = [ms.loc[ei,'PriceDiff'] if ms.loc[ei, 'Hold']==1 else 0 for ei in ms.index]
ms['avg50']= ms['Close'].rolling(50).mean()
ms['avg20']= ms['Close'].rolling(20).mean()

ms.Close.plot()
ms.avg20.plot()
ms.avg50.plot()



ms['Wealth']= ms['Profit'].cumsum()
print(ms.head())

#ms['Wealth'].plot()
#plt.axhline(y=0, color = 'red')


print(ms['Wealth'].mean(), ms['Wealth'].std(ddof=1))



z = (ms['Return'] -ms['Return'].mean())/ms['Return'].std(ddof=1)

#stats.probplot(z, dist='norm', plot=plt)

#plt.show()

iwm= pd.read_csv('./data/iwm.csv', index_col=0)
iwm_close = iwm['Close']
iwm_data = DataFrame()
iwm_data['close']= iwm_close
iwm_data['log_return']= np.log(iwm_data['close']).diff()
iwm_data.fillna(0, inplace = True)
print(iwm_data.tail())
print(iwm_data['log_return'].tail(22).mean())
print(iwm_data['log_return'].tail(22).std())
# down 8.8% in 11 days



def calc_probability(mv_pct, days, symbol, tail_days) :
    df = pd.read_csv('./data/{}.csv'.format(symbol), index_col=0)
    data = df['Close']
    data_logreturn = np.log(data).diff()
    data_logreturn_rolling = data_logreturn.rolling(days).sum()
    mean = data_logreturn_rolling.tail(tail_days).mean()
    std = data_logreturn_rolling.tail(tail_days).std()
    temp = norm.cdf(np.log(1+mv_pct),mean, std)
    pvalue = temp if mv_pct<0 else 1-temp
    return mean, std, pvalue

def calc_mv_pct(zscore, days, symbol, tail_days) :
    df = pd.read_csv('./data/{}.csv'.format(symbol), index_col=0)
    data = df['Close']
    data_logreturn = np.log(data).diff()
    data_logreturn_rolling = data_logreturn.rolling(days).sum()
    mean = data_logreturn_rolling.tail(tail_days).mean()
    std = data_logreturn_rolling.tail(tail_days).std()
    #temp = norm.cdf(mean - zscore*std,mean, std)
    #pvalue = temp if mv_pct<0 else 1-temp
    return mean, std, mean - zscore*std, np.exp(mean - zscore*std)-1

days=17

mv_pct= -0.11
tail_days=500


x,y,z = calc_probability(mv_pct,days, 'iwm', tail_days)
zscore = (np.log(1+mv_pct) - x)/y
print('Sample {5} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, probability move over {3:.2f}% is {4:.2f}%, zscore: {6:.2f}'.format(days,x*100, y*100, mv_pct*100, z*100, tail_days, zscore))

zscore =1.65
x2,y2,z2,z2exp = calc_mv_pct(zscore, days, 'iwm', tail_days)
print('Sample {4} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, zscore is {3:.2f}, mv_down pct: {5:.2f}%'.format(days,x2*100, y2*100, zscore, tail_days,z2exp*100))
zscore =2
x2,y2,z2, z2exp = calc_mv_pct(zscore, days, 'iwm', tail_days)
print('Sample {4} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, zscore is {3:.2f}, mv_down pct: {5:.2f}%'.format(days,x2*100, y2*100, zscore, tail_days,z2exp*100))
