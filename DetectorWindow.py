import time

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
import scipy.signal
import gxipy as gx
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import MyWindow
import utils


class Detector(MyWindow.Ui_MainWindow):

    def __init__(self):
        # 继承Ui_MainWindow，并对Ui_MainWindow进行初始化
        super().__init__()
        # 在Detector类中调用，来初始化主窗口，使Detector获得MyWindow.Ui_MainWindow类的属性
        self.setupUi(MainWindow)
        self.retranslateUi(MainWindow)


        self.function()

    def function(self):
        print('成功启用function')

        '''相机导入操作'''
        self.pushButtonRe.clicked.connect(self.opencamera) # 点击'打开设备'时，触发opencamera函数
        self.pushButtonClear.clicked.connect(self.textBrowser_tab1.clear)  # 清空消息栏
        # 如果检测不到相机，那么return之后的代码不会运行。故而无相机时只有reload和clear有效。
        if self.opencamera() == 0:
            return
        '''相机参数设置部分'''
        self.lineEditExposureTime.editingFinished.connect(self.changeexposuretime)

        '''连续采集'''
        # 获取连续采集，采集图像按钮
        self.pushButtonGetimage_tab1_1.clicked.connect(self.continousAcquistion)
        # 连续采集，开始采集图片并处理
        self.pushButtonStart_tab1_1.clicked.connect(self.continousAcquistionStart)
        # 连续采集，停止采集图片并处理
        self.pushButtonStop_tab1_1.clicked.connect(self.continousAcquistionStop)
        '''单次采集'''

        '''自定义采集'''

    #相机导入函数
    def opencamera(self):
        # 输出获取图片的初始化信息
        self.textBrowser_tab1.append('====================')
        self.textBrowser_tab1.append('正在调用相机,初始化中...')
        self.textBrowser_tab1.append('====================')
        # 创建设备管理器
        self.device_manager = gx.DeviceManager()
        # 更新设备列表
        self.dev_num, self.dev_info_list = self.device_manager.update_device_list()
        self.textBrowser_tab1.append(f"当前可用设备数量:{self.dev_num}\n")
        if self.dev_num == 0:
            self.textBrowser_tab1.append("没有找到相机设备。\n请检查设备链接情况或稍后再试!\n")
            return 0

        # 当没有相机设备时，return之后的代码不会运行，即下列代码不会运行。
        str_index = self.dev_info_list[0].get("index")  # 获取设备基本信息列表
        self.cam = self.device_manager.open_device_by_index(str_index)  # 打开设备
        # 检测是否以及打开设备，并进行输出

        # 默认触发方式为连续采集，设置默认曝光时间为10000us，增益0
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.cam.ExposureTime.set(10000)  # 默认曝光时间10000us
        self.cam.Gain.set(0)
        self.textBrowser_tab1.append('已经默认设置为连续采集模式，曝光时间为10000us')

        # 显示默认曝光时间
        exposuretime_value = self.cam.ExposureTime.get()
        self.lineEditExposureTime.setText(str(exposuretime_value))    # 获取相机曝光时间并显示在lineEdit中,为什么不能提取？
        # 显示默认增益数值
        gain_value = self.cam.Gain.get()
        self.lineEditGain.setText(str(gain_value))
    def changeexposuretime(self):
        exposuretime = self.lineEditExposureTime.text()
        exposuretime_value = float(exposuretime)
        self.cam.ExposureTime.set(exposuretime_value)
        self.textBrowser_tab1.append(f'设置曝光时间为{self.lineEditExposureTime.text()}us')
        # 报错原因是在opencamera中，对self.cam的赋值出现了问题，赋值的是一个局部变量。

    # 连续采集部分
    def continousAcquistion(self):
        # 触发方式为连续采集
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.textBrowser_tab1.append('更改为连续采集模式')


    def continousAcquistionStart(self):
        self.textBrowser_tab1.append('开始连续 采集连接成功')
    def continousAcquistionStop(self):
        self.textBrowser_tab1.append('停止连续采集连接成功')




if __name__ == '__main__':
    #获取UIC窗口操作权限
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    #调自定义的界面,即获取从QT导出的界面.py文件
    Ui = Detector()
    # Ui.setupUi(MainWindow) #不需要这一行了，这一行移到super().__init__()后，在创建Detector类时就对创建的进行初始化了

    #显示窗口并释放资源
    MainWindow.show()
    sys.exit(app.exec_())