import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 20, 100)  # Create a list of evenly-spaced numbers over the range
#plt.plot(x, np.sin(x))       # Plot the sine ofpyth each x point

#plt.show()                   # Display the plot

data = {'a': np.arange(50),
        'c': np.random.randint(0, 50, 50),
        'd': np.random.randn(50)}
data['b'] = data['a'] + 10 * np.random.randn(50)
data['d'] = np.abs(data['d']) * 100

#plt.scatter('a', 'b', c='c', s='d', data=data)
plt.scatter('a','b', data=data)
plt.xlabel('entry a')
plt.ylabel('entry b')
plt.show()

a = np.array([[1,2],[3,4],[5,6]]) 
b = np.array([[11,12],[13,14]]) 
print(np.dot(b,a))