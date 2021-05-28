import pandas as  pd
import numpy as np 
from scipy.stats import norm 
import matplotlib.pyplot as plt

data = pd.DataFrame()
data['Population'] = [47, 48, 85, 20, 19, 13, 72, 16, 50, 60,]

sampleWR = data['Population'].sample(5, replace = True)
print(type(data['Population']))

p_mean = data['Population'].mean()
p_var = data['Population'].var(ddof=0)

print('Population mean is ', p_mean)
print('Population variance is', p_var)


a_sample = data['Population'].sample(10, replace=True)
sample_mean = a_sample.mean()
sample_var = a_sample.var()
print('Sample mean is ', sample_mean)
print('Sample variance is', sample_var)


sample_length = 500
sample_variance_collection0=[data['Population'].sample(50, replace=True).var(ddof=0) for i in range(sample_length)]
sample_variance_collection1=[data['Population'].sample(50, replace=True).var(ddof=1) for i in range(sample_length)]

print ('Sample collection mean 0 is ', pd.DataFrame(sample_variance_collection0)[0].mean())
print ('Sample collection mean 1 is ', pd.DataFrame(sample_variance_collection1)[0].mean())

Fstsample = pd.DataFrame(np.random.normal(10,5,size=30))
print('sample mean is ', Fstsample[0].mean())
print('sample SD is ', Fstsample[0].std(ddof=1))

meanlist =[]
for t in range(10000):
    sample = pd.DataFrame(np.random.normal(10,5,size=30))
    meanlist.append(sample[0].mean())

collection = pd.DataFrame()
collection['meanlist'] = meanlist

print(collection['meanlist'].mean())
print(collection['meanlist'].var())

#collection['meanlist'].hist(bins=100, density=True, figsize=(15,8))



sample_size = 100
samplemeanlist = []
apop =  pd.DataFrame([1, 0, 1, 0, 1])
for t in range(10000):
    sample = apop[0].sample(sample_size, replace=True)  # small sample size
    samplemeanlist.append(sample.mean())

acollec = pd.DataFrame()
#acollec['meanlist'] = samplemeanlist
#acollec.hist(bins=100, density=True, figsize=(15,8))

#plt.show()

ms =pd.read_csv('.\data\MSFT.csv')
print(ms.head())

ms['LogReturn'] = np.log(ms['Close']).shift(-1)-np.log(ms['Close'])

size = ms['LogReturn'].shape[0]
mean=ms['LogReturn'].mean()
std= ms['LogReturn'].std(ddof=1)/(size**0.5)

z_left= norm.ppf(0.05)
z_right=norm.ppf(0.95)

interval_left = mean+z_left*std
interval_right = mean+z_right*std

print('90% confidence interval is ', (interval_left, interval_right))




ms['LogReturn'].plot(figsize=(20, 8))
plt.axhline(0, color='red')
#plt.show()

sample_mean = ms['LogReturn'].mean()
sample_std = ms['LogReturn'].std(ddof=1)
n=ms['LogReturn'].shape[0]

zscore = sample_mean/(sample_std/n**0.5)
print('mean, std, n,  zscore is ',sample_mean, sample_std, n, zscore)

alpha = 0.25

zleft = norm.ppf(alpha/2,0,1)
zright=-zleft
print(zleft, zright)

print('At significant level of {}, shall we reject: {}'.format(alpha, zscore>zright or zscore<zleft))

zright = norm.ppf(1-alpha, 0,1)
pvalue = 1- norm.cdf(zscore, 0, 1)
print('one tail test, shall we reject: ', zscore>zright, pvalue)

