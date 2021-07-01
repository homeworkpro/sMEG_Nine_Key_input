import tkinter
import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import pandas as pd
import time
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model
from emg import EMG_filter

mSerial = serial.Serial('COM3', 115200)
i = 0
q = Queue(maxsize=0)
r = Queue(maxsize=0)

def Serial():
    global q
    global r
    while True:
        n = mSerial.inWaiting()
        if n:
            valueRead = mSerial.readline()
            valueRead = valueRead.decode().replace("\r", "").replace("\n", "")
            dat = valueRead.split(",")
            dat = list(map(int, dat))
            # print(dat)
            q.put(dat)
            channel1.append(dat[0])
            channel1.pop(0)
            channel2.append(dat[1])
            channel2.pop(0)
            channel3.append(dat[2])
            channel3.pop(0)
            channel4.append(dat[3])
            channel4.pop(0)
            channel5.append(dat[4])
            channel5.pop(0)


def plotData():
    global i
    data = q.get()
    # print(data)
    if i < historyLength:
        data1[i] = data[0]
        data2[i] = data[1]
        data3[i] = data[2]
        data4[i] = data[3]
        data5[i] = data[4]

        i = i + 1
    else:
        data1[:-1] = data1[1:]
        data1[i - 1] = data[0]
        data2[:-1] = data2[1:]
        data2[i - 1] = data[1]
        data3[:-1] = data3[1:]
        data3[i - 1] = data[2]
        data4[:-1] = data2[1:]
        data4[i - 1] = data[1]
        data5[:-1] = data3[1:]
        data5[i - 1] = data[2]

    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)
    curve4.setData(data4)
    curve5.setData(data5)

def isMotion():
    global result
    min1 = np.mean(channel1)
    min2 = np.mean(channel2)
    if min1<=40 and min2 <= 40:
        result = "放松"
        p.set(result)
        l.update()
        return False
    return True

def processDetect():
    global isDetecting
    # if not isMotion():
    #     return
    while True:
        if not isDetecting:
            detect(channel1, channel2, channel3,channel4,channel5)
            # isDetecting = False


def detect(channel1, channel2, channel3,channel4, channel5):
    global result
    global isDetecting
    sample = emg_filter(channel1, channel2, channel3)
    # print(sample.shape)
    sample = np.expand_dims(sample, axis=3)
    prediction = model.predict(sample)
    # a = np.array([1,2])
    # print(np.max(a))
    # print(prediction[0])
    result = np.where(prediction[0] == np.max(prediction[0]))[0][0]
    if(result==0):
        result = "大拇指"
    elif(result ==1):
        result = "食指"
    elif(result==2):
        result = "中指"
    elif(result==3):
        result = "无名指"
    elif(result == 4):
        result = "小拇指"
    #print(result)

    p.set(result)
    l.update()
    isDetecting = False


def emg_filter(channel1, channel2, channel3):
    global interval
    channels = []
    for i in range(interval):
        sample = [channel1[i], channel2[i], channel3[i]]
        channels.append(sample)
    res = [channels]
    return np.asarray(res)

app = pg.mkQApp()  # 建立app
win = pg.GraphicsWindow()  # 建立窗口
win.setWindowTitle(u'pyqtgraph逐点波形图')
win.resize(800, 500)

historyLength = 100  # 横坐标长度
data1 = array.array('i')  # 可动态改变数组的大小，double型数组
data1 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
data2 = array.array('i')  # 可动态改变数组的大小，double型数组
data2 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
data3 = array.array('i')  # 可动态改变数组的大小，double型数组
data3 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
data4 = array.array('i')  # 可动态改变数组的大小，double型数组
data4 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
data5 = array.array('i')  # 可动态改变数组的大小，double型数组
data5 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
p1 = win.addPlot()  # 把图p加入到窗口中
p1.showGrid(x=True, y=True)
p1.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p1.setLabel(axis='left', text='y/ V')  # 靠左
p1.setLabel(axis='bottom', text='x/ point')
p1.setTitle('semg')  # 表格名字
curve1 = p1.plot()  # 绘制图形
curve1.setData(data1)
p2 = win.addPlot()  # 把图p加入到窗口中
p2.showGrid(x=True, y=True)
p2.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p2.setLabel(axis='left', text='y/ V')  # 靠左
p2.setLabel(axis='bottom', text='x/ point')
p2.setTitle('semg')  # 表格名字
curve2 = p2.plot()  # 绘制图形
curve2.setData(data2)
win.nextRow()
p3 = win.addPlot()  # 把图p加入到窗口中
p3.showGrid(x=True, y=True)
p3.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p3.setLabel(axis='left', text='y/ V')  # 靠左
p3.setLabel(axis='bottom', text='x/ point')
p3.setTitle('semg')  # 表格名字
curve3 = p3.plot()  # 绘制图形
curve3.setData(data3)
p4 = win.addPlot()  # 把图p加入到窗口中
p4.showGrid(x=True, y=True)
p4.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p4.setLabel(axis='left', text='y/ V')  # 靠左
p4.setLabel(axis='bottom', text='x/ point')
p4.setTitle('semg')  # 表格名字
curve4 = p4.plot()  # 绘制图形
curve4.setData(data4)
p5 = win.addPlot()  # 把图p加入到窗口中
p5.showGrid(x=True, y=True)
p5.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p5.setLabel(axis='left', text='y/ V')  # 靠左
p5.setLabel(axis='bottom', text='x/ point')
p5.setTitle('semg')  # 表格名字
curve5 = p5.plot()  # 绘制图形
curve5.setData(data5)
if mSerial.isOpen():
    print("open success")
    mSerial.flushInput()
else:
    print("open failed")
    serial.close()  # 关闭端口
interval = 120
channel1 = [0 for x in range(interval)]
channel2 = [0 for x in range(interval)]
channel3 = [0 for x in range(interval)]
channel4 = [0 for x in range(interval)]
channel5 = [0 for x in range(interval)]
isDetecting = False
emgFilter = EMG_filter()
model = keras.models.load_model('./model/meg_model.h5')
model.summary()
window = tkinter.Tk()
window.title('gesture predictor')
window.geometry('500x300')
p = tkinter.StringVar()
p.set("hello")
l = tkinter.Label(window, show=None, textvariable=p, width=10, height=2)
l.pack()
lock = threading.Lock()
th1 = threading.Thread(target=Serial)
th1.start()
th2 = threading.Thread(target=processDetect)
th2.start()
timer = pg.QtCore.QTimer()
timer.timeout.connect(plotData)  # 定时刷新数据显示
timer.start(1)  # 多少毫秒调用一次
window.mainloop()

app.exec_()