import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


dice = pd.DataFrame({'Col1':[1,2,3,4,5,6]})


print(dice.sample(2, replace = True).sum())

results = [dice.sample(2, replace=True ).sum()[0] for i in range(5000)]


freq = pd.DataFrame({'Col':results})['Col'].value_counts()
print(type(pd.DataFrame({'Col':results})['Col']))
sort_freq = freq.sort_index()
print((freq))
#sort_freq['Rate']=sort_freq[]/500
#print(sort_freq)
relative_freq = sort_freq/5000
#relative_freq.plot(kind='bar', color='blue')
#plt.show()

x_dis = pd.DataFrame(index = [2,3,4,5,6,7,8,9,10,11,12])
x_dis['Prob']=[1,2,3,4,5,6,5,4,3,2,1]
x_dis['Prob']=x_dis['Prob']/36
#print(x_dis)

mean = pd.Series(x_dis.index*x_dis['Prob']).sum()
var =pd.Series(((x_dis.index-mean)**2)*x_dis['Prob']).sum()

var2 = pd.Series(x_dis.index**2*x_dis['Prob']).sum() - pd.Series(x_dis.index*x_dis['Prob']).sum()**2

#print(mean, var, var2)

ms=pd.read_csv('./data/MSFT.csv')
#ms['LogReturn'] = np.log(ms['Close']).shift(-1) - np.log(ms['Close'])
ms['LogReturn'] = (ms['Close'].shift(-1) - ms['Close'])/ms['Close']

mu = ms['LogReturn'].mean()
sigma = ms['LogReturn'].std()

print(mu, sigma, ms['LogReturn'].min(), ms['LogReturn'].max())
#print(ms.head())




density = pd.DataFrame()
density['x'] = np.arange(ms['LogReturn'].min()-0.01, ms['LogReturn'].max()+0.01, 0.001)

density['pdf']=stats.norm.pdf(density['x'], mu, sigma)

density['cdf']=stats.norm.cdf(density['x'], mu, sigma)



print(ms.loc['2020-01-02':'2020-01-31', 'LogReturn'])

#ms['LogReturn'].hist(bins=50, figsize=(15, 8))
#plt.plot(density['x'], density['pdf'], color='red')
plt.plot(density['x'], density['cdf'], color='green')
#plt.show()

z= (ms['LogReturn']-mu)/sigma
#stats.probplot(z, dist='norm', plot = plt )
plt.show()

prob_return1 = stats.norm.cdf(-0.4, mu*220, sigma*(220**0.5))
print('The Probability down 40pct in 1 year is ', prob_return1)

prob_return2 = stats.norm.ppf(0.05, mu, sigma)
print('The VAR is ', prob_return2)

#print(mu, sigma)

