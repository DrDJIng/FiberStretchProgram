import matplotlib.pyplot as plt
import numpy as np
import time

fig = plt.figure()
ax = fig.add_subplot(111)

# some X and Y data
x = np.arange(10000)
y = np.random.randn(10000)

li, = ax.plot(x, y)

# draw and show it
ax.relim()
ax.autoscale_view(True,True,True)
fig.canvas.draw()
plt.ion()
plt.show()

# loop to update the data
update = 0
while True:
    y[:-10] = y[10:]
    y[-10:] = np.random.randn(10)

    # set the new data
    li.set_ydata(y)
    plt.draw()
    update += 1
    print(update)
    plt.pause(0.01)