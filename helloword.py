from scipy.optimize import minimize
import pandas as pd
import matplotlib.pyplot as plt

def eqn(x):
  return x**2 + x + 2

mymin = minimize(eqn, 0, method='BFGS')

print(mymin)
<<<<<<< HEAD
print('test tets and test 2121')

arr = [1,2,3,4,5,6,-2]

arr2 = [x*3 for x in arr if x%2==0]
print(arr2)

mydataset = {
  'cars': ["BMW", "Volvo", "Ford"],
  'passings': [3, 7, 2]
}

myvar = pd.DataFrame(mydataset)

print(myvar)

df = pd.read_csv('./data/data.csv')
dfcorr = df.corr()
print(type(dfcorr))
print(dfcorr)
#print(df['Mix'].mean())
#print(df['Mix'].std())

#print(df['Equity'].mean())
#print(df['Equity'].std())
df['Duration'].plot(kind = 'hist')
##plt.show()

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

