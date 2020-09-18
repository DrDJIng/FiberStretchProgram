import csv
import numpy as np
import matplotlib.pyplot as plt

#%%
file = open(r'F:\Guth data\17092020 12.csv')
data_array = csv.reader(file)
zipped_data = list(data_array)

#%%
# Unzip list
data = [[i for i, j, k, l in zipped_data],
            [j for i, j, k, l in zipped_data],
            [k for i, j, k, l in zipped_data],
            [l for i, j, k, l in zipped_data]]

time = np.array(data[0])
force = np.array(data[1])
length = np.array(data[2])
signal = np.array(data[3])
#%%
fig = plt.figure()
ax = fig.add_axes([0, 900, 0, 10])
ax.plot(time, force)
ax.set_xticklabels('')
ax.set_yticklabels('')
plt.show()