from numpy.lib.polynomial import polyval
import pandas as  pd 
import matplotlib.pyplot as plt
from pandas.core import series
from pandas.core.frame import DataFrame
import scipy.stats as stats
import numpy as np 
from scipy.stats import norm 

class StockMoveProb:
    #calculate odds of stock up/down certain pct during specific period, tail_days is the number of latest dates to get mean and std. 
    #e.g. calc probability of IWM down 10% during 15 trading days, use latest 1000 data points to measure
    def calc_probability(self, mv_pct, days, symbol, tail_days) :
        df = pd.read_csv('./data/{}.csv'.format(symbol), index_col=0)
        data = df['Adj Close']
        data_logreturn = pd.Series(map(np.log, data)).diff()
        data_logreturn_rolling = data_logreturn.rolling(days).sum()
        mean = data_logreturn_rolling.tail(tail_days).mean()
        std = data_logreturn_rolling.tail(tail_days).std()
        temp = norm.cdf(np.log(1+mv_pct),mean, std)
        pvalue = temp if mv_pct<0 else 1-temp
        return mean, std, pvalue

    #calculate up/down pct of stock during specific period for certain zscore, tail_days is the number of latest dates to get mean and std. 
    #e.g.  Given zscore = 2, calcuate up/down pct for IWM during 15 trading days, use latest 1000 data points to measure
    def calc_mv_pct(self, zscore, days, symbol, tail_days) :
        df = pd.read_csv('./data/{}.csv'.format(symbol), index_col=0)
        data = df['Adj Close']
        data_logreturn = np.log(data).diff()
        data_logreturn_rolling = data_logreturn.rolling(days).sum()
        data_logreturn_rolling.fillna(0, inplace=True)
        mean = data_logreturn_rolling.tail(tail_days).mean()
        std = data_logreturn_rolling.tail(tail_days).std()
        #temp = norm.cdf(mean - zscore*std,mean, std)
        #pvalue = temp if mv_pct<0 else 1-temp
        return mean, std, mean - zscore*std, np.exp(mean - zscore*std)-1

    # calc gain after major pull back
    # e.g. after MDY down 10% in 22 days, calculate gain after22*2days
    def calc_gain_after_down(self, down_mv_pct, days, symbol, tail_days ):
        df = pd.read_csv('./data/{}.csv'.format(symbol), index_col=0)
        data = df['Adj Close']
        data_logreturn = np.log(data).diff()
        data_logreturn_rolling = data_logreturn.tail(tail_days).rolling(days).sum()
        #df3 = DataFrame(data_logreturn_rolling)
        #path_save = './data/temp_iwm.csv'
        #df3.to_csv(path_save)
        filter_idx=[]
        filter_val =[]
        i=0
        while i < (len(data_logreturn_rolling.index)):
            if data_logreturn_rolling.iloc[i]<np.log(1+down_mv_pct) and i+days<len(data_logreturn_rolling.index): 
                filter_idx.append(data_logreturn_rolling.index[i+1])
                idx = data_logreturn_rolling.index[i+1]
                start = data_logreturn.index.get_loc(idx)                
                v= data_logreturn.iloc[start:start+4*days].sum()
                filter_val.append(v)
                i+=days
            i+=1

        res = pd.Series(data=filter_val, index=filter_idx)
        pd.set_option('display.max_rows', res.size+1)
        print(res)
        
        return res.mean(), res.std()

stock = StockMoveProb()
days=22
mv_pct= -0.10
tail_days=10000
symbol = 'mdy'


x,y,z = stock.calc_probability(mv_pct,days,symbol, tail_days)
zscore = (np.log(1+mv_pct) - x)/y
print('Sample {5} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, probability move over {3:.2f}% is {4:.2f}%, zscore: {6:.2f}'.format(days,x*100, y*100, mv_pct*100, z*100, tail_days, zscore))

zscore =1.65
x2,y2,z2,z2exp = stock.calc_mv_pct(zscore, days, symbol, tail_days)
print('Sample {4} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, zscore is {3:.2f}, mv_down pct: {5:.2f}%'.format(days,x2*100, y2*100, zscore, tail_days,z2exp*100))
zscore =2
x2,y2,z2, z2exp = stock.calc_mv_pct(zscore, days, symbol, tail_days)
print('Sample {4} tail days: {0} day average is {1:.2f}%, std is {2:.2f}%, zscore is {3:.2f}, mv_down pct: {5:.2f}%'.format(days,x2*100, y2*100, zscore, tail_days,z2exp*100))

x,y = stock.calc_gain_after_down(mv_pct, days, symbol, tail_days)
print('pct gain/loss after down {3}% in {2} days: mean: {0}, std: {1}'.format(x,y, days,mv_pct*100))