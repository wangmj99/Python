from numpy.core.defchararray import mod
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import statsmodels.api as smf
import statsmodels.formula.api as sm
import scipy.stats as stats

ms = pd.read_csv('./data/MSFT.csv', index_col=0)

ms['logReturn'] = np.log(ms['Close']).shift(1)- np.log(ms['Close'])
ms['logVolDiff'] = np.log(ms['Volume']).shift(1)- np.log(ms['Volume'])

print(ms.corr())

#from pandas.plotting import scatter_matrix
#sm = scatter_matrix(ms, figsize=(10, 10))

b0=212.8719
b1=-0.6052/1000000
ms['guess'] = b0+b1*ms['Volume']
ms['obvError'] = ms['Close'] - ms['guess']

# plt.figure(figsize=(10,10))
# plt.title('Sum of sqaured error is {}'.format((((ms['obvError'])**2)).sum()))
# plt.scatter(ms['Volume'], ms['Close'], color='g', label='Observed')
# plt.plot(ms['Volume'], ms['guess'], color='red', label='GuessResponse')
# plt.legend()
# plt.xlim(ms['Volume'].min()-2, ms['Volume'].max()+2)
# plt.ylim(ms['Close'].min()-2, ms['Close'].max()+2)

# plt.plot(ms.index, ms['obvError'], color='purple')
# plt.axhline(y=0, color ='red')

# ms.plot(kind='scatter', x='Volume', y='Close', color ='green')

z= (ms['obvError']-ms['obvError'].mean())/ms['obvError'].std(ddof=1)
print(type(z))
stats.probplot(z, dist='norm', plot=plt)

#plt.show()



'''
x= ms['Volume']/1000000
y = ms['Close']
x=smf.add_constant(x)
#print(x)
model = smf.OLS(y,x)
result = model.fit()
#print(result.summary())
'''

x1 = ms['Open']
y1 = ms['Close']

x1 = smf.add_constant(x1)

# model1 = smf.OLS(y1,x1)
# result1 = model1.fit()

model2 = sm.ols(formula = 'Close~Open',data = ms).fit()
print (model2.summary())

#print(result1.summary())
#print(result1.params[0], result1.params[1])
