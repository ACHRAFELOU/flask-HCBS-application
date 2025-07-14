import serial
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
from drawnow import *
import pyautogui
import cv2
import keyboard
trace = [0.0] * 128  # Create a list with 128 zeros

ser = serial.Serial(port='COM3', baudrate=9600, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

plt.ion()
sensors = 128
x = dict([(s, []) for s in range(0, sensors)])
plt.figure(figsize=(12, 8))
def get_color(sensor_num):
    colors = plt.cm.tab20c(np.linspace(0, 1, 32))
    return colors[sensor_num % 32]
def get_linestyle(sensor_num):
    linestyles = ['o-', '*-', '--', '-']
    return linestyles[sensor_num  % 4]
def Makefigure():

    plt.clf()  # Clear the current figure

    plt.suptitle("Live Data of the Breast Temperature", fontsize=12)
    plt.subplots_adjust(hspace=0.2)  # Adjust the vertical space between subplots
    plt.grid(True)
    plt.xlabel('Time (seconds)')

    for i in range(4):
        plt.subplot(2, 2, i+1)
        plt.grid(True)
        plt.ylabel("Temperature °C", fontsize=10)
        start = i * 32
        end = start + 32
        for sensor_num, sensor_data in x.items():
            if start <= sensor_num < end:
                color = get_color(sensor_num)
                linestyle = get_linestyle(sensor_num)
                plt.plot(sensor_data,linestyle, label=f'Sensor {sensor_num + 1}',color=color)

            # Add the legend directly on the curve

        plt.title(f'Quadrant {i+1}', fontsize=8)
        plt.legend(loc='upper left', bbox_to_anchor=(0.8, 0.5), ncol=3, fontsize=6, fancybox=True, framealpha=0.2,
                   shadow=True, borderaxespad=0.41)

    plt.tight_layout()

timeStart = time.time()
is_running = True
while is_running :
    timeDelay = time.time() - timeStart

    while ser.inWaiting() == 0:
        pass

    line = ser.readline().decode('utf-8')
    line = line.split(',')

    if len(line) >= 32:
        line = [x.strip() for x in line]

    for i in range(sensors):
        trace[i] = float(line[i])

    for s in range(sensors):
        x[s].append(trace[s])

    drawnow(Makefigure)


    # Limit the number of data points for smoother display
    for sensor_data in x.values():
        if len(sensor_data) > 1000:
            sensor_data.pop(0)

    screenshot_path = "C:/Users/a.elouerghi/Desktop/images thermiques créées/screenshot_0.png"
    pyautogui.screenshot(screenshot_path)

    if keyboard.is_pressed('q'):
        is_running = False
ser.close()