from pandas.core.frame import DataFrame
from scipy.optimize import minimize
import pandas as pd
import matplotlib.pyplot as plt
from array import *
import numpy as np
from scipy.sparse.sputils import matrix
from  datetime import datetime

from statsmodels.tsa.vector_ar.vecm import coint_johansen

def eqn(x):
  return x**2 + x + 2

mymin = minimize(eqn, 0, method='BFGS')

#print(mymin)


arr = [1,2,3,4,50,6,-2]

arr2 = [x*3 for x in arr if x%2==0]
print(arr2)

arr3 = np.array(arr)
print(arr3.mean(),arr3.std())

mydataset = {
  'cars': ["BMW", "Volvo", "Ford"],
  'passings': [3, 7, 2]
}

myvar = pd.DataFrame(mydataset)






nums = [i for i in range(1,1001)]
string = "Practice Problems to Drill List Comprehension in Your Head."

#List comprehension Quesitons
#Find all of the numbers from 1–1000 that are divisible by 8
q1 = [i for i in nums if i%8==0]

#Find all of the numbers from 1–1000 that have a 6 in them
q2 = [i for i in nums if '6' in str(i)] 

#Count the number of spaces in a string
q3 = len([c for c in string if c== ' '])

#4. Remove all of the vowels in a string
q4 = "".join([c for c in string if c not in ['a', 'e', 'o', 'i', 'u']])

#7. Use a nested list comprehension to find all of the numbers from 1–1000 that are divisible by any single digit besides 1 (2–9)
q7 = [i for i in nums if True in [True for divisor in range(2,10) if i%divisor == 0]]

print('test tets and test 1213')


arr1 = array('i', [1,5,6,2])
print(arr1)

m = map(len, ['app', 'test'])
print(type(m))
print(list(m))



myseries = pd.Series([1,4,0,7,5], index=['a','b','c','d','e'])
for i in range(len(myseries.index)):
  print(myseries.index[i] , myseries.iloc[i])

a = np.array([1,2,3])
b = np.array([2,2,2])
c = np.array([3,1,1])
matrix = np.column_stack((a,b,c))
print(matrix)

A = np.array([[2,1,-1],[-3,-1,2],[-2,1,2]])
b = np.array([[8],[-11],[-3]])

#print (np.linalg.solve(A, b))

list1 = pd.Series([10,20,30]).rename('col1')
list1.index = ['a', 'b', 'c']
list2 = pd.Series([20,30,40]).rename('col2')
list2.index = ['a', 'b', 'c']
list4 = pd.Series([30,50,420]).rename('col3')
list4.index = ['a', 'b', 'c']


df2 = None
if df2 is None: df2 = pd.DataFrame(list1)


df2 = pd.concat([df2,  list2, list4], axis=1)

#df2['total'] = df2.sum(axis=1)
print (df2)
#lm = lambda x: x.sum()
lm = lambda x: 1 if abs(100- x.sum())<0.001 else (0 if x.sum()<100 else -1)
df2['update'] = df2.apply(lm, axis= 1)



idx = pd.date_range('1/1/2021', periods=99, freq='D')
s1 = pd.Series([x for x in range(1,100)])
s1.index = idx
s2 = s1.resample('M').agg(lambda x: (x[-1]-x[0])/x[0])
dt = pd.to_datetime("2020-12-31")
ilocidx = s1.index.get_loc(dt, method='bfill')

print('ilocidx: ' + str(ilocidx))
print(s1.index[0])

