import matplotlib.pyplot as plt
from pandas import read_csv
from os.path import dirname, abspath
from os import getcwd
import numpy as np
from matplotlib.animation import FuncAnimation

"""
Draw images and animated graphs.

Velocity sensor: average velocity in a 1 unit movement
Rotation sensor: average rotation in a 90 rotation
UltraSonic sensor: distance to the nearest object
"""

def hcsr(folder):
    pd = read_csv(f"{folder}\\hcsr04.log", header=None)

    rawdata = pd[0].tolist()

    # construct sub lists at break points
    data = []
    sublist = []
    for item in rawdata:
        if item != "------" and item != "-----":
            sublist.append(float(item))
            
        elif len(sublist) > 0:
            sublist = []
            data.append(sublist)
    
    # remove strings from data
    cleandata = []
    for item in rawdata:
        if item != "------" and item != "-----" and item != "":
            cleandata.append(float(item))

    fig = plt.figure(figsize=(8,6))
    ax = plt.axes()

    x = list(range(0, len(data[0])))
    avg = sum(data[0])/len(data[0])
    avg_line = [avg,]*len(data[0])

    ax.scatter(x, data[0], color='red')
    ax.plot(x, avg_line, 'g')

    ax.set_xlabel('Sample')
    ax.set_ylabel('Depth (cm)')
    ax.set_title('Average depth from sample spread')

    ax.axhline(avg, color="gray", ls=":")

    twin_ax = ax.twinx()
    twin_ax.set_yticks([avg])
    twin_ax.set_ylim(ax.get_ylim())

    plt.savefig(f"{folder}\\hcsr_depth.png")


def mpuVelocity(folder):
    pd = read_csv(f"{folder}\\velocity.log", header=None)

    rawdata = pd[0].tolist()

    # construct sub lists at break points
    data = []
    sublist = []
    for item in rawdata:
        if item != "------":
            sublist.append(float(item))
            
        elif len(sublist) > 0:
            data.append(sublist)
            sublist = []


    # convert orientation over time into rotation over time
    data_velocity = []
    for sublist in data:
        new_sublist = []
        curr = sublist[0]
        for item in sublist:
            change = item - curr
            curr = item
            new_sublist.append(change)
        data_velocity.append(new_sublist)


    # constrain all sublists to length of 5 (shortest)
    for idx, sublist in enumerate(data_velocity):
        if len(sublist) > 5:
            data_velocity[idx] = sublist[:5]

    # average sublists to get average list
    y = data_velocity[0].copy()
    error_max = data_velocity[0].copy()
    error_min = data_velocity[0].copy()

    for sublist in data_velocity[1:]:
        for idx, item in enumerate(sublist):
            y[idx] += item
            y[idx] /= 2

            if item > error_max[idx]:
                error_max[idx] = item
            elif item < error_min[idx]:
                error_min[idx] = item

    fig = plt.figure(figsize=(8,6))
    ax = plt.axes()

    x = list(range(0, len(y)))
    ax.plot(x, y)
    ax.plot(x, error_max, 'r--')
    ax.plot(x, error_min, 'r--')

    ax.set_xlabel('Sample')
    ax.set_ylabel('Acceleration / sample')
    ax.set_title('Velocity over time')

    ax2 = ax.twinx()
    ax2.set_ylim([0, 5])
    ax2.set_ylabel('Velocity')

    plt.savefig(f"{folder}\\mpu6050_velocity.png")

def smallestAngle(currentAngle, targetAngle):
    # Subtract the angles, constraining the value to [0, 360)
    diff = ( targetAngle - currentAngle) % 360

    # If we are more than 180 we're taking the long way around.
    # Let's instead go in the shorter, negative direction
    if diff > 180 :
        diff = -(360 - diff)

    return diff

def mpuRotation(folder):
    # average rotation

    pd = read_csv(f"{folder}\\mpu6050.log", header=None)

    rawdata = pd[0].tolist()

    # construct sub lists at break points
    data = []
    sublist = []
    for item in rawdata:
        if item != "------":
            sublist.append(float(item))
            
        elif len(sublist) > 0:
            data.append(sublist)
            sublist = []

    # convert orientation over time into rotation over time
    data_rotation = []
    for sublist in data:
        new_sublist = []
        curr = sublist[0]
        for item in sublist:
            change = smallestAngle(curr, item)
            curr = item
            new_sublist.append(change)
        data_rotation.append(new_sublist)

    # constrain all sublists to length of 7 (shortest)
    for idx, sublist in enumerate(data_rotation):
        if len(sublist) > 6:
            data_rotation[idx] = sublist[:6]

    y_positive = None
    error_max_positive = None
    error_min_positive = None

    y_negative = None
    error_max_negative = None
    error_min_negative = None

    for sublist in data_rotation[1:]:
        # if line ends negative
        if sublist[-1] < 0:
            if not y_negative:
                y_negative = sublist.copy()
                error_max_negative = sublist.copy()
                error_min_negative = sublist.copy()

            # negative rotation
            for idx, item in enumerate(sublist):
                y_negative[idx] += item
                y_negative[idx] /= 2

                if item > error_max_negative[idx]:
                    error_max_negative[idx] = item
                elif item < error_min_negative[idx]:
                    error_min_negative[idx] = item

        else:
            if not y_positive:
                y_positive = sublist.copy()
                error_max_positive = sublist.copy()
                error_min_positive = sublist.copy()

            # positive rotation
            for idx, item in enumerate(sublist):
                y_positive[idx] += item
                y_positive[idx] /= 2

                if item > error_max_positive[idx]:
                    error_max_positive[idx] = item
                elif item < error_min_positive[idx]:
                    error_min_positive[idx] = item

    fig = plt.figure(figsize=(8,6))
    ax = plt.axes()

    x = list(range(0, len(y_negative)))
    
    ax.plot(x, y_positive)
    ax.plot(x, error_max_positive, 'r--')
    ax.plot(x, error_min_positive, 'r--')

    ax.plot(x, y_negative)
    ax.plot(x, error_max_negative, 'r--')
    ax.plot(x, error_min_negative, 'r--')

    ax.set_xlabel('Sample')
    ax.set_ylabel('Rotation / sample')
    ax.set_title('Rotation over time')

    ax2 = ax.twinx()
    ax2.set_ylim([-100.0, 100.0])
    ax2.set_ylabel('Orientation')

    plt.savefig(f"{folder}\\mpu6050_rotation.png")

if __name__ == "__main__":
    folder_list = ["1 - clean 1", "2 - obstacles 1", "3 - clean 2", "4 - obstacles 2"]

    for run in folder_list:
        folder = f"{getcwd()}\\testing\\logs\\{run}"
        mpuRotation(folder)
        mpuVelocity(folder)
        hcsr(folder)