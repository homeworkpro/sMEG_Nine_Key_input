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
from pykeyboard import *

mSerial = serial.Serial('COM3', 115200)
i = 0
q = Queue(maxsize=0)
r = Queue(maxsize=0)

def Serial():
    global q
    global r
    global isMotionN
    global isBacktoRest
    global isinWindow
    while True:
        n = mSerial.inWaiting()
        if n:
            valueRead = mSerial.readline()
            valueRead = valueRead.decode().replace("\r", "").replace("\n", "")
            dat = valueRead.split(",")
            dat = list(map(int, dat))
            dat[0] = dat[0]-100
            # print(dat)
            q.put(dat)
            # channel.append(dat)
            # channel.pop(0)
            lock2.acquire()
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
            channel6.append(dat[5])
            channel6.pop(0)

            mean1 = (channel1[118] + channel2[118] + channel3[118]) / 3
            mean2 = (channel4[118]+channel5[118]+channel6[118])/3
            if event.is_set():
                lock2.release()
                continue
            elif mean1 <= 40 and mean2 <= 40:
                # result = "放松"
                # p.set(result)
                # l.update()
                if not isBacktoRest:
                    if not isinWindow:
                        isBacktoRest = True
                isMotionN= 0
            elif mean1 <= 40:
                #print("right")
                isMotionN=2
                event.set()
            elif mean2 <= 40:
                #print("left")
                isMotionN=1
                event.set()
            lock2.release()

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
        data6[i] = data[5]

        i = i + 1
    else:
        data1[:-1] = data1[1:]
        data1[i - 1] = data[0]
        data2[:-1] = data2[1:]
        data2[i - 1] = data[1]
        data3[:-1] = data3[1:]
        data3[i - 1] = data[2]
        data4[:-1] = data4[1:]
        data4[i - 1] = data[3]
        data5[:-1] = data5[1:]
        data5[i - 1] = data[4]
        data6[:-1] = data6[1:]
        data6[i - 1] = data[5]

    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)
    curve4.setData(data4)
    curve5.setData(data5)
    curve6.setData(data6)

def isMotion():
    global result
    #data = channel[118]
    # min1 = (data[0] + data[1]+data[2])/3
    # min2 = (data[3] + data[4]+data[5])/3
    min1 = (channel1[118]+channel2[118]+channel3[118])/3
    min2 = (channel4[118]+channel5[118]+channel6[118])/3
    #print("calculate")
    #print("hello")
    if min1 <= 80 and min2 <= 80:
        if result=="放松":
            return False
        result = "放松"
        uith = threading.Thread(target=freshUi, args=(result,))
        uith.start()
        return False
    # elif min1<=40:
    #     print("right")
    #     return 2
    # elif min2<=40:
    #     print("left")
    #     return 1

def processDetect():
    global isDetecting
    global resultvalue
    global windowStartTime
    global windowStopTime
    global isinWindow
    global isBacktoRest
    global isMotionN
    global result
    #global isselecting
    processDetect.lastresult = 0
    while True:
            #print("thread 2")
        #isMotionN = isMotion()
            while not event.is_set():
                if not isMotion():
                    print("thread start wait...")
                    event.wait()
            #当从放松状态改变，开启0.5s时间窗口
            if not isinWindow:
                if not isMotion() and not isBacktoRest:
                    isBacktoRest = True
                    result = "放松"
                    uith = threading.Thread(target=freshUi, args=(result,))
                    uith.start()
                    print("back to rest")
                    time.sleep(0.5)
                    event.clear()
                    continue
                #print("getting ready")
                currenttime = time.time()
                stoptimestamp = int(round((currenttime - windowStopTime) * 1000))
                #if not ((not (stoptimestamp>=1000)) and isBacktoRest):
                if isBacktoRest and stoptimestamp>=500:
                    isinWindow = True
                    print("begin")
                    windowStartTime = time.time()
                    #print("begin time:"+str(windowStartTime))
            if event.is_set():
                if isinWindow:
                    #if not isDetecting:
                    #print("continue")
                    if isMotionN == 1:
                        #print("start")
                        resultvalue = detect_left(channel1, channel2, channel3)
                        #print("left")
                    elif isMotionN == 2:
                        resultvalue = detect_right(channel4, channel5, channel6)
                        print("right")
                    result = resultvalue
                    if(result==0 or result==9):
                        result = "大拇指"
                    elif(result ==1 or result==8):
                        result = "食指"
                    elif(result==2 or result==7):
                        result = "中指"
                    elif(result==3 or result==6):
                        result = "无名指"
                    elif(result == 4 or result==5):
                        result = "小拇指"
                    elif(result==10 or result==11):
                        result = "握拳"
                    if processDetect.lastresult != result:
                        #print(result)
                        uith = threading.Thread(target=freshUi, args=(result,))
                        uith.start()
                        # p.set(result)
                        # l.update()
                        #print("end render")
                    else:
                        processDetect.lastresult = result
                    currenttime = time.time()
                    #print("current time:" + str(currenttime))
                    begintimestamp = int(round((currenttime - windowStartTime) * 1000))
                    if (begintimestamp >= 400):
                        if (resultvalue==10):
                            k.tap_key(k.down_key)
                        elif (resultvalue==9):
                            k.tap_key(k.space)
                        elif (resultvalue==11):
                            k.tap_key(k.up_key)
                        else:
                            k.tap_key(str(resultvalue + 1))
                        print("end")
                        print(resultvalue)
                        isinWindow = False
                        isBacktoRest = False
                        windowStopTime = time.time()
                        isMotion()
                        time.sleep(0.5)
                        event.clear()



def detect_left(channel1, channel2, channel3):
    global result
    global isDetecting
    sample = emg_filter(channel1, channel2, channel3)
    # print(sample.shape)
    sample = np.expand_dims(sample, axis=3)
    #print("start predict")
    prediction = model_left.predict(sample)
    #print("stop predict")
    # a = np.array([1,2])
    # print(np.max(a))
    # print(prediction[0])
    result = np.where(prediction[0] == np.max(prediction[0]))[0][0]
    theresultvalue = result
    # if(result==0):
    #     result = "大拇指"
    # elif(result ==1):
    #     result = "食指"
    # elif(result==2):
    #     result = "中指"
    # elif(result==3):
    #     result = "无名指"
    # elif(result == 4):
    #     result = "小拇指"
    # print(result)
    # p.set(result)
    # l.update()
    # time.sleep(0.1)
    # isDetecting = False
    #print("predict done")
    if theresultvalue == 5:
        return 11
    return theresultvalue

def detect_right(channel4, channel5, channel6):
    global result
    global isDetecting
    sample = emg_filter(channel4, channel5, channel6)
    # print(sample.shape)
    sample = np.expand_dims(sample, axis=3)
    prediction = model_right.predict(sample)
    # a = np.array([1,2])
    # print(np.max(a))
    # print(prediction[0])
    result = np.where(prediction[0] == np.max(prediction[0]))[0][0]
    theresultvalue = result
    #print(result)
    # if(result==0):
    #     result = "大拇指"
    # elif(result ==1):
    #     result = "食指"
    # elif(result==2):
    #     result = "中指"
    # elif(result==3):
    #     result = "无名指"
    # elif(result == 4):
    #     result = "小拇指"
    # #print(result)
    # p.set(result)
    # l.update()
    # isDetecting = False
    if theresultvalue == 5:
        #print("fist")
        return 10
    return 9-theresultvalue

def freshUi(result):
    global p,l
    lock.acquire()
    p.set(result)
    l.update()
    lock.release()

def emg_filter(channel1, channel2, channel3):
    global interval
    channels = []
    for i in range(interval):
        sample = [channel1[i], channel2[i], channel3[i]]
        channels.append(sample)
    res = [channels]
    return np.asarray(res)

#plot emg signals
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
data6 = array.array('i')  # 可动态改变数组的大小，double型数组
data6 = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
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
p6 = win.addPlot()  # 把图p加入到窗口中
p6.showGrid(x=True, y=True)
p6.setRange(xRange=[0, historyLength], yRange=[0, 200], padding=0)
p6.setLabel(axis='left', text='y/ V')  # 靠左
p6.setLabel(axis='bottom', text='x/ point')
p6.setTitle('semg')  # 表格名字
curve6 = p6.plot()  # 绘制图形
curve6.setData(data6)

#open the serial
if mSerial.isOpen():
    print("open success")
    mSerial.flushInput()
else:
    print("open failed")
    serial.close()  # 关闭端口


#initialize the data structure for storing data from each channel
interval = 120
channel1 = [0 for x in range(interval)]
channel2 = [0 for x in range(interval)]
channel3 = [0 for x in range(interval)]
channel4 = [0 for x in range(interval)]
channel5 = [0 for x in range(interval)]
channel6 = [0 for x in range(interval)]

#global parameter for detecting
isDetecting = False
isinWindow = False
isBacktoRest = True
isMotionN = 0
result = "放松"
windowStartTime = time.time()
windowStopTime = time.time()
resultvalue=0

#load keras model
model_left = keras.models.load_model('model/left_hand.h5')
model_left.summary()
model_right = keras.models.load_model('model/right_hand.h5')
model_right.summary()

#draw ui to display detecting result
window = tkinter.Tk()
k = PyKeyboard()
window.title('gesture predictor')
window.geometry('500x300')
p = tkinter.StringVar()
p.set("hello")
l = tkinter.Label(window, show=None, textvariable=p, width=10, height=2)
l.pack()
lock = threading.Lock()
lock2 = threading.Lock()
event = threading.Event()
th1 = threading.Thread(target=Serial)
th1.start()
th2 = threading.Thread(target=processDetect)
th2.start()
timer = pg.QtCore.QTimer()
timer.timeout.connect(plotData)  # 定时刷新数据显示
timer.start(1)  # 多少毫秒调用一次
window.mainloop()

app.exec_()