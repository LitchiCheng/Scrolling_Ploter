import sys
import numpy as np
import pyqtgraph as pg
from PySide6 import QtWidgets, QtCore

import zmq
import threading

class RealTimePlot(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plotWidget = pg.PlotWidget()
        self.setCentralWidget(self.plotWidget)

        # 设置背景颜色为白色
        self.plotWidget.setBackground("w")
        pg.setConfigOption("useOpenGL", True)

        # 添加两条曲线
        self.curve1 = self.plotWidget.plot(pen=pg.mkPen(width=2.5, color='r'), name='c1')
        self.curve2 = self.plotWidget.plot(pen=pg.mkPen(width=2.5, color='b'), name='c2')

        # 初始化数据
        self.time = []
        self.data1 = []
        self.data2 = []

        # # 设置定时器
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update_plot)
        # self.timer.start(100)  # 每100毫秒更新一次

        # 添加暂停按钮
        self.pauseButton = QtWidgets.QPushButton("Pause", self)
        self.pauseButton.setCheckable(True)
        self.pauseButton.clicked.connect(self.toggle_pause)
        self.pauseButton.setGeometry(10, 10, 60, 30)
        self.plot_on = True

        self.t1 = threading.Thread(target=self.update_plot)

        # 初始化zmq
        serverIp = "192.168.192.5"
        port = 5535
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.serverIp = serverIp
        self.port = port
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect(f"tcp://{serverIp}:{port}")

        self.t1.start()
        
    
    def toggle_pause(self):
        if self.pauseButton.isChecked():
            self.plot_on = True
            self.pauseButton.setText("Resume")
        else:
            self.plot_on = False
            self.pauseButton.setText("Pause")
    
    def update_plot(self):
        while True:
            if self.plot_on:
                msg = self.socket.recv_string()
                vars = msg.split("|")
                time1 = float(vars[0])
                y1 = float(vars[1])
                y2 = float(vars[2])
                # print("%f %f %f" % (time1, y1, y2))

                # 模拟新数据
                self.time.append(time1)
                new_value1 = y1
                new_value2 = y2
                
                self.data1.append(new_value1)
                self.data2.append(new_value2)

                # 保持最新的100个数据点
                points_num = 1000
                if len(self.data1) > points_num:
                    self.data1 = self.data1[-points_num:]
                    self.data2 = self.data2[-points_num:]
                    self.time = self.time[-points_num:]

                self.curve1.setData(self.time, self.data1)
                self.curve2.setData(self.time, self.data2)
                self.plotWidget.setXRange(self.time[0], self.time[-1])

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec())
