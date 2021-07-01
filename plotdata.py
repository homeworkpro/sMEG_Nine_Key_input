import tkinter

import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model
from emg import EMG_filter
import time
from tkinter import *

i = 0
q = Queue(maxsize=0)


def Serial():
    global q
    global isDetecting
    while True:
        n = mSerial.inWaiting()
        if n:
            valueRead = mSerial.readline()
            valueRead = valueRead.decode().replace("\r", "").replace("\n", "")
            dat = valueRead.split(",")
            dat = list(map(int, dat))
            # print(dat)
            q.put(dat[0])
            channel1.append(dat[0])
            channel1.pop(0)
            channel2.append(dat[1])
            channel2.pop(0)


def processDetect():
    global isDetecting
    while True:
        if not isDetecting:
            detect(channel1, channel2, channel3)
            # isDetecting = False


def detect(channel1, channel2, channel3):
    global result
    global isDetecting
    sample = emg_filter(channel1, channel2, channel3)
    # print(sample.shape)
    sample = np.expand_dims(sample, axis=3)
    prediction = model.predict(sample)
    # a = np.array([1,2])
    # print(np.max(a))
    # print(prediction[0])
    result = np.where(prediction[0] == np.max(prediction[0]))[0]
    #print(result)
    v.set(result)
    w.update()
    isDetecting = False


def emg_filter(channel1, channel2, channel3):
    channels = []
    for i in range(200):
        sample = [emgFilter.filter(channel1[i]), emgFilter.filter(channel2[i]), 0]
        channels.append(sample)
    res = [channels]
    return np.asarray(res)


def plotData():
    global i
    if i < historyLength:
        data[i] = q.get()
        i = i + 1
    else:
        data[:-1] = data[1:]
        data[i - 1] = q.get()
    curve.setData(data)


if __name__ == "__main__":
    channel1 = [0 for x in range(200)]
    channel2 = [0 for x in range(200)]
    channel3 = [0 for x in range(200)]
    isDetecting = False
    emgFilter = EMG_filter()
    model = keras.models.load_model('model/left_hand.h5')
    model.summary()
    app = pg.mkQApp()  # 建立app
    win = pg.GraphicsWindow()  # 建立窗口
    win.setWindowTitle(u'pyqtgraph逐点波形图')
    win.resize(800, 500)
    data = array.array('i')  # 可动态改变数组的大小，double型数组
    historyLength = 100  # 横坐标长度
    root = tkinter.Tk()
    result = "放松"
    data = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
    p = win.addPlot()  # 把图p加入到窗口中
    p.showGrid(x=True, y=True)
    p.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
    p.setLabel(axis='left', text='y/ V')  # 靠左
    p.setLabel(axis='bottom', text='x/ point')
    p.setTitle('semg')  # 表格名字
    curve = p.plot()  # 绘制图形
    curve.setData(data)
    portx = 'COM3'
    bps = 115200
    # 串口执行到这已经打开， 再用open命令会报错
    mSerial = serial.Serial(portx, int(bps))
    if mSerial.isOpen():
        print("open success")
        mSerial.flushInput()
    else:
        print("open failed")
        serial.close()  # 关闭端口
    th1 = threading.Thread(target=Serial)
    th1.start()
    th2 = threading.Thread(target=processDetect)
    th2.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData)  # 定时刷新数据显示
    timer.start(10)  # 多少毫秒调用一次
    v = tkinter.StringVar()
    w = tkinter.Label(root, textvariable=v)
    v.set(result)
    w.pack()
    root.mainloop()
    app.exec_()
