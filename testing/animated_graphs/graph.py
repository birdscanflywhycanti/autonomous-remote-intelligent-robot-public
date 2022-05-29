import matplotlib.pyplot as plt
from pandas import read_csv
from os.path import dirname, abspath
import numpy as np
from matplotlib.animation import FuncAnimation 

script_path = abspath(dirname(__file__))

pd = read_csv(f"{script_path}/test.csv", header=None)

data = pd[0].tolist()

x, y = [], []

fig = plt.figure()
   
# marking the x-axis and y-axis
axis = plt.axes(xlim=(0, len(data)+1), ylim=(min(data)-1, max(data)+1))

line, = axis.plot([], [], lw=1)

def init():
    line.set_data([], [])
    return line,

def animate(i):
    x.append(i)
    y.append(data[i])

    line.set_xdata(x)
    line.set_ydata(y)
    return line,

anim = FuncAnimation(fig, animate, init_func=init, frames=len(data), interval=20, blit=True)

anim.save(f'{script_path}/test.mp4', writer='ffmpeg', fps = 30)
