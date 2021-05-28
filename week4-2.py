import pandas as pd 
#import statsmodels.api as smf
import statsmodels.formula.api as smf
import numpy as np 
import matplotlib.pyplot as plt 

import warnings
warnings.filterwarnings("ignore") 

aord = pd.read_csv('./data/indice/AORD.csv', index_col=0)
nikkei = pd.read_csv('./data/indice/Nikkei225.csv', index_col=0)
hsi = pd.read_csv('./data/indice/HSI.csv', index_col=0)
daxi = pd.read_csv('./data/indice/DAXI.csv', index_col=0)
cac40 = pd.read_csv('./data/indice/CAC40.csv', index_col=0)
sp500 = pd.read_csv('./data/indice/SP500.csv', index_col=0)
dji = pd.read_csv('./data/indice/DJI.csv', index_col=0)
nasdaq = pd.read_csv('./data/indice/Nasdaq.csv', index_col=0)
spy = pd.read_csv('./data/indice/SPY.csv', index_col=0)

indicepanel=pd.DataFrame(index = spy.index)

indicepanel['spy'] = spy['Open'].shift(-1)-spy['Open']
indicepanel['spy_lag1'] = spy['Open'] - spy['Open'].shift(1)
indicepanel['sp500']=sp500["Open"]-sp500['Open'].shift(1)
indicepanel['nasdaq']=nasdaq['Open']-nasdaq['Open'].shift(1)
indicepanel['dji']=dji['Open']-dji['Open'].shift(1)

indicepanel['cac40']=cac40['Open']-cac40['Open'].shift(1)
indicepanel['daxi']=daxi['Open']-daxi['Open'].shift(1)

indicepanel['aord']=aord['Close']-aord['Open']
indicepanel['hsi']=hsi['Close']-hsi['Open']
indicepanel['nikkei']=nikkei['Close']-nikkei['Open']

indicepanel['Price']=spy['Open']


indicepanel = indicepanel.fillna(method = 'ffill')
indicepanel = indicepanel.dropna()
print(indicepanel.isnull().sum())

path_save = './data/indice/indicepanel.csv'
#indicepanel.to_csv(path_save)

Train = indicepanel.iloc[-7000:-3500, :]
Test = indicepanel.iloc[-3500:, :]


#from pandas.plotting import scatter_matrix
#sm = scatter_matrix(Train, figsize=(15, 15))
#plt.show()

corr_array = Train.iloc[:,:-1].corr()['spy']

formula = 'spy~spy_lag1+sp500+nasdaq+dji+cac40+aord+daxi+nikkei+hsi'
lm = smf.ols(formula=formula, data=Train).fit()
lm.summary()

print(lm.summary())

Train['PredictedY'] = lm.predict(Train)
Test['PredictedY'] = lm.predict(Test)

#print(Train.head())
#plt.scatter(Train['spy'], Train['PredictedY'])
#plt.show()


# RMSE - Root Mean Squared Error, Adjusted R^2
def adjustedMetric(data, model, model_k, yname):
    data['yhat'] = model.predict(data)
    SST = ((data[yname] - data[yname].mean())**2).sum()
    SSR = ((data['yhat'] - data[yname].mean())**2).sum()
    SSE = ((data[yname] - data['yhat'])**2).sum()
    r2 = SSR/SST
    adjustR2 = 1 - (1-r2)*(data.shape[0] - 1)/(data.shape[0] -model_k -1)
    RMSE = (SSE/(data.shape[0] -model_k -1))**0.5
    return adjustR2, RMSE

def assessTable(test, train, model, model_k, yname):
    r2test, RMSEtest = adjustedMetric(test, model, model_k, yname)
    r2train, RMSEtrain = adjustedMetric(train, model, model_k, yname)
    assessment = pd.DataFrame(index=['R2', 'RMSE'], columns=['Train', 'Test'])
    assessment['Train'] = [r2train, RMSEtrain]
    assessment['Test'] = [r2test, RMSEtest]
    return assessment

# Get the assement table fo our model
#print(assessTable(Test, Train, lm, 9, 'spy'))

def calc(df, name ):
    #Profit of Signal-based strategy
    df['Order'] = [1 if sig>0 else -1 for sig in df['PredictedY']]
    df['Profit'] = df['Order'] * df['spy']
    df['Wealth'] = df['Profit'].cumsum()
    print("Total profit of {} made: {}".format(name, df['Profit'].sum()))

    #show(df, name)

    #Calculate sharpe ratio
    #Add start price for sharpe calculation
    df['Wealth2'] = df['Wealth']+df.loc[df.index[0], 'Price']
    df['Return'] = df['Wealth2'] /(df['Wealth2'].shift(1))-1
    daily_r = df['Return'].dropna()

    print("Daily Sharpe Ratio of {} is {}".format(name, daily_r.mean()/daily_r.std(ddof=1)))
    print("Yearly Sharpe Ratio of {} is {}".format(name, (252**0.5)*daily_r.mean()/daily_r.std(ddof=1)))

    #Calculate max drawdown
    df['Peak'] = df['Wealth'].cummax()
    df['Drawdown'] = (df['Peak']-df['Wealth'])/df['Peak']
    print("Maximum Drawdown in {} is {}".format(name, df['Drawdown'].max()))

    #Calculate SPY max drawdown
    df['spyWealth'] = df['spy'].cumsum()+df.loc[df.index[0], 'Price']
    df['spyPeak'] = df['spyWealth'].cummax()
    df['spyDrawdown'] = (df['spyPeak']-df['spyWealth'])/df['spyPeak']
    print("Maximum SPY Drawdown in {} is {}".format(name, df['spyDrawdown'].max()))

def show(df1, name1):
    #plot strategy profit along with SPY
    plt.figure(figsize =(20,15))
    plt.title('Performance')
    plt.plot(df1['Wealth'], color='green', label='Singal strategy')
    plt.plot(df1['spy'].cumsum(), color='red', label ='B&H stratey')
    plt.legend()
    plt.show()

calc(Train, 'Train')

print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
calc(Test, 'Test')
show(Test,'Test')

