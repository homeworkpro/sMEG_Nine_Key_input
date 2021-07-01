# visualize the arduino
import serial
import matplotlib.pyplot as plt
import atexit
import time
from IPython import display
from drawnow import *

values = []
plt.ion()

serialArduino = serial.Serial('COM3', 115200)


def plotValues():
    plt.cla()
    plt.title('EMG siganl from Arduino')
    plt.grid(True)
    plt.ylabel('Amplitute')
    plt.ylim([0, 300])
    plt.plot(values, 'r', label='EMG')
    plt.legend(loc='upper right')
    # display.clear_output(wait=True)
    # plt.pause(0.0000000001)


def doAtExit():
    serialArduino.close()
    print("Close serial")
    print("serialArduino.isOpen() = " + str(serialArduino.isOpen()))


atexit.register(doAtExit)  # 程序退出时，回调函数
print("serialArduino.isOpen() = " + str(serialArduino.isOpen()))

# 预加载虚拟数据
for i in range(50):
    values.append(0)

i = 0
while True:
    while serialArduino.inWaiting() == 0:
        pass
    valueRead = serialArduino.readline()
    valueRead = valueRead.decode().replace("\r", "").replace("\n", "")
    data = valueRead.split(",")
    data = list(map(int, data))
    # print(data)
    values.append(data[0])
    values.pop(0)
    # plotValues()
    drawnow(plotValues)

window = tkinter.Tk()
window.title('gesture predictor')
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