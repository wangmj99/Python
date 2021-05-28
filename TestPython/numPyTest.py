
# coding: utf-8

# # Import data
# In this Jupyter Notebook, you will learn how to import data from CSV into Jupyter Notebook

# In[1]:


#import the package "Pandas" into Jupyter Notebook
import pandas as pd
import matplotlib.pyplot as plt



# In[2]:


#We import the stock data of Facebook into Jupyter Notebook. The CSV file is located in the folder called "Data" in your Workspace
#We then name the DataFrame name as 'fb'
fb = pd.read_csv('./data/facebook.csv')



# ### Instruction
# Now is your turn to import the stock price of Microsoft (microsoft.csv), of which the CSV is located in the same folder, and rename the Dataframe in "ms". 

# In[3]:


ms = pd.read_csv('./data/msft.csv', index_col=0)

print("data type is %s" % (type(ms.loc['2019-12-18':'2020-11-30'])))

print(ms[['Open','Close']].head())

print(ms.head())

ms['PriceDiff']=ms['Close']-ms['Close'].shift(1)



ms['Return']=ms['PriceDiff']/ms['Close']

ms['MA20'] =ms['Close'].rolling(20).mean()
ms['MA50'] =ms['Close'].rolling(50).mean()

result = []
for value in ms['PriceDiff']:
    if value>0:
        result.append(1)
    else:
        result.append(0)

ms['Direction'] = result
#ms['Direction'] = [1 if ms['PriceDiff'].loc[ei]>0 else 0 for ei in ms.index]

ms['Share'] = [1 if ms.loc[ei,'MA20']>ms.loc[ei,'MA50'] else 0 for ei in ms.index]
ms['TClose'] = ms['Close'].shift(-1)
ms['Profit']= [ms.loc[ei, 'TClose']-ms.loc[ei,'Close'] if ms.loc[ei, 'Share'] == 1 else 0 for ei in ms.index]
ms['Wealth']=ms['Profit'].cumsum()

start = ms.loc['2019-12-31','Close']
ms['YTD']= ms['Close']-start

# run this cell to ensure Microsoft's stock data is imported
print(ms.tail())
plt.figure(figsize=(16, 12))
ms.loc['2020-01-02':'2020-12-31','YTD'].plot()
ms.loc['2020-01-02':'2020-12-31','Wealth'].plot()
#ms.loc['2020-01-02':'2020-12-31','MA50'].plot()
plt.show()
#print(ms.shape)

