import numpy as np
from matplotlib import pyplot as plt

def main():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.relim()
    ax.autoscale_view(True,True,True)
    plt.ion()
    plt.show()

    x = np.arange(-50, 51)
    for pow in range(1,5):   # plot x^1, x^2, ..., x^4
        y = [Xi**pow for Xi in x]
        plt.plot(x, y)
        plt.draw()
        plt.pause(0.001)

if __name__ == '__main__':
    main()