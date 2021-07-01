import tkinter

import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import pandas as pd
import time
from tkinter import *

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
            r.put(dat)


def plotData():
    global i
    data = q.get()
    # print(data)
    if i < historyLength:
        data1[i] = data[0]
        data2[i] = data[1]
        data3[i] = data[2]

        i = i + 1
    else:
        data1[:-1] = data1[1:]
        data1[i - 1] = data[0]
        data2[:-1] = data2[1:]
        data2[i - 1] = data[1]
        data3[:-1] = data3[1:]
        data3[i - 1] = data[2]

    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)


# 储存数据在.csv文件中
def recordtoCSV(self):
    global start
    while start:
        if not self.Flag:
            break
        if r.empty():
            continue
        data = []
        while not r.empty():
            data.append(r.get())
        pd_data = pd.DataFrame(data)
        # print(data)
        pd_data.to_csv(file, index=False, header=False, mode="a")
        time.sleep(3)
    print("stop")


filepath = "./dataset/"
file = ""
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
if mSerial.isOpen():
    print("open success")
    mSerial.flushInput()
else:
    print("open failed")
    serial.close()  # 关闭端口

start = False

class recordThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.Flag=True
        self.Parm=0

    def run(self):
        recordtoCSV(self)

    def setFlag(self,parm):
        self.Flag=parm

    def setParm(self,parm):
        self.Parm =parm

    def getParm(self):
        return self.Parm

def start_record():
    global file
    global  start
    start = True
    filename = p.get()
    # filename = ""
    file = filepath + filename + ".csv"
    th2 = recordThread()
    th2.start()


def stop_record():
    print("close!!!!!")
    global start
    start = False
    #th2.setFlag(False)


window = tkinter.Tk()
window.title('EMG Controller')
window.geometry('500x300')
p = tkinter.StringVar()
p.set("hello")
e = tkinter.Entry(window, show=None, textvariable=p)
e.pack()
b1 = tkinter.Button(window, text="start record", width=10, height=2, command=start_record)
b1.pack()
b2 = tkinter.Button(window, text="stop record", width=10, height=2, command=stop_record)
b2.pack()
lock = threading.Lock()
th1 = threading.Thread(target=Serial)
th1.start()
#th2 = recordThread()
timer = pg.QtCore.QTimer()
timer.timeout.connect(plotData)  # 定时刷新数据显示
timer.start(1)  # 多少毫秒调用一次
window.mainloop()

app.exec_()
