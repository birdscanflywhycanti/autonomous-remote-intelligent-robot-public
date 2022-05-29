# generate a random gaussian graph

# import the required libraries 
import random 
import matplotlib.pyplot as plt 
    
# store the random numbers in a list 
data = [] 
mu = 100
sigma = 50
    
for i in range(100): 
    data.append(random.gauss(mu, sigma)) 
        
# plotting a graph 
plt.plot(data) 
plt.show()

# save data to file
import csv
with open('test.csv','w') as f:
    writer = csv.writer(f)
    writer.writerows(zip(data))
