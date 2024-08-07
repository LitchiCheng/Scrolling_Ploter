""" 
QChart动态绘图
"""
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QTimer, QPointF  # QPointF在QtCore中
from PySide6.QtWidgets import QApplication
import sys
import math
import numpy as np

import zmq
import threading

class SinWaveChart(QChart):
    def __init__(self):
        super().__init__()
        # super().setUseOpenGL(True)
        # 创建一个序列
        self.series = QLineSeries()
        self.series1 = QLineSeries()
        self.addSeries(self.series)
        self.addSeries(self.series1)

        # 创建坐标轴
        self.axisX_ = QValueAxis()
        self.axisY_ = QValueAxis()
        self.addAxis(self.axisX_, Qt.AlignBottom)
        self.addAxis(self.axisY_, Qt.AlignLeft)
        self.series.attachAxis(self.axisX_)
        self.series.attachAxis(self.axisY_)
        self.series1.attachAxis(self.axisX_)
        self.series1.attachAxis(self.axisY_)
        self.axisX_.setTickCount(10)
        
        self.resize(1500,500)

        self.t1 = threading.Thread(target=self.run)

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
    
    def updateYAxisRange(self, axis, series_list):
        min_y = float('inf')
        max_y = float('-inf')
        for series in series_list:
            for point in series.points():
                min_y = min(min_y, point.y())
                max_y = max(max_y, point.y())
        axis.setRange(min_y, max_y)
    
    def updateXAxisRange(self, axis, series_list):
        min_y = float('inf')
        max_y = float('-inf')
        for series in series_list:
            for point in series.points():
                min_y = min(min_y, point.x())
                max_y = max(max_y, point.x())
        axis.setRange(min_y, max_y)
        # print("minx %f %f %f" % (min_y, max_y, ((max_y-min_y)/1000000.0)))

    def run(self):
        while True:
            msg = self.socket.recv_string()
            vars = msg.split("|")
            time1 = float(vars[0])
            y1 = float(vars[1])
            y2 = float(vars[2])
            print("%f %f %f" % (time1, y1, y2))
                
            self.series.append(QPointF(time1, y1))
            self.series1.append(QPointF(time1, y2))

            # 只显示最新
            if self.series.count() > 100: 
                self.series.remove(0)

            self.updateXAxisRange(self.axisX_, [self.series])
            self.updateYAxisRange(self.axisY_, [self.series, self.series1])

if __name__ == "__main__":
    app = QApplication(sys.argv)

    chart = SinWaveChart()
    chart.legend().hide()
    chart.setTitle("Dynamic wave")

    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.Antialiasing, True)

    chart_view.show()

    sys.exit(app.exec())
