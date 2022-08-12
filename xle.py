import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm

def gen_dataframe(ticker):
    filename = './data/{}.csv'.format(ticker)
    df = pd.read_csv(filename, index_col = 0)
    df.columns = df.columns.map(lambda col: col.lower())
    df['dailyReturn'] = df['adj close']/(df['adj close'].shift(1)) -1
    df['dailyreturntemp'] = df['dailyReturn']+1
    df['month'] = df.index.astype(str).str[:7]
    df.dropna()
    return df

def gen_monthly_ts(df):  
    df_monthly = df.groupby('month')['dailyreturntemp'].prod()-1
    return df_monthly

def printMonthlyStats(ticker, alpha, VAR, ts_monthly):
    round_decimal = 5
    mean = round(ts_monthly.mean(),round_decimal)
    std = round(ts_monthly.std(),round_decimal)
    print('{} monthly return mean: {}, std: {}'.format(ticker, mean, std))
    zscore = stats.norm.ppf(alpha)
    print('{} percent monthly return range: ({}, {})'.format(100-alpha*100*2, mean+std*zscore, mean-std*zscore ))
    print('{} percent monthly VAR is {} '.format(VAR, stats.norm.ppf(1-VAR/100, mean, std)))
    print(ts_monthly.tail(12))

def plotMonthly(ts_monthly):
    zc = (ts_monthly-ts_monthly.mean())/ts_monthly.std()
    ts_monthly.plot()
    #ts_monthly.hist(bins=50, density=True,figsize=(7,7))
    #stats.probplot(zc, dist='norm', plot=plt)

ticker = 'IWM'
ticker_df = gen_dataframe(ticker)
ticker_monthly = gen_monthly_ts(ticker_df)
printMonthlyStats(ticker, 0.025, 95, ticker_monthly)
#plotMonthly(ticker_monthly)
plt.show()


# xle = pd.read_csv('./data/^GSPC.csv', index_col = 0)
# xle.columns = xle.columns.map(lambda col: col.lower())


# xle['dailyReturn'] = xle['adj close']/(xle['adj close'].shift(1)) -1

# xle['dailyreturntemp'] = xle['dailyReturn']+1

# xle['month'] = xle.index.astype(str).str[:7]
# xle_monthly = xle.groupby('month')['dailyreturntemp'].prod()-1
# print(xle_monthly.tail(12))
# print('montly mean {}, std {}'.format(xle_monthly.mean(), xle_monthly.std()))
# zc = (xle_monthly-xle_monthly.mean())/xle_monthly.std()
# #stats.probplot(zc, dist='norm', plot=plt)
# xle_monthly.hist(bins=50, density=True,figsize=(10,10))
# #xle_monthly.plot()
# plt.show()
# zleft = stats.norm.ppf(0.05)
# zright = stats.norm.ppf(0.95)
# print('1st monthly interval {}, {}, {}'.format(zleft, xle_monthly.mean()+zleft*xle_monthly.std(), xle_monthly.mean()+zright*xle_monthly.std()))
# print('95% VAR is: {}'.format(stats.norm.ppf(0.05, xle_monthly.mean(), xle_monthly.std())))

# xle = xle.dropna()
# print(xle.tail())
# mean = (xle['dailyReturn'].mean())
# std = (xle['dailyReturn'].std())
# zscore = (xle['dailyReturn']-mean)/std

# mean_monthly = mean*253/12
# std_monthly = std*((253/12)**0.5)



# print('interval {}, {}, {}'.format(zleft, mean_monthly+zleft*std_monthly, mean_monthly+zright*std_monthly))
# #xle['dailyReturn'].plot()
# #plt.show()