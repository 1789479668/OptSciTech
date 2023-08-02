import io

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
from scipy.signal import find_peaks
from scipy.optimize import fsolve
import gxipy as gx
import numpy as np
import matplotlib.pyplot as plt
import MyWindow


class Detector(MyWindow.Ui_MainWindow):

    def __init__(self):
        # 继承Ui_MainWindow，并对Ui_MainWindow进行初始化
        super().__init__()
        # 在Detector类中调用，来初始化主窗口，使Detector获得MyWindow.Ui_MainWindow类的属性
        self.setupUi(MainWindow)
        self.retranslateUi(MainWindow)
        self.acquisitionloop = False    # 初始化采集循环控制
        # self.mode1loop = False  # 初始化连续采集控制

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

        '''图像获取'''
        # 采集图像按钮
        self.pushButtonGetimage_tab1_1.clicked.connect(self.continuousAcquisition)
        # 停止采集图片
        self.pushButtonGetimageStop_tab1_1.clicked.connect(self.continuousAcquisitionStop)

        '''连续采集'''
        # 开始接受图片并进行图像处理并展示图片
        self.pushButtonStart_tab1_1.clicked.connect(self.mode1_Start)



        '''单次采集'''

        '''自定义采集'''

    #相机导入函数
    def opencamera(self):
        if hasattr(self, 'cam') and self.cam is not None:
            self.textBrowser_tab1.append("相机设备已经被打开!\n")
            return
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
        # 检测是否打开了设备
        str_index = self.dev_info_list[0].get("index")  # 获取设备基本信息列表
        self.cam = self.device_manager.open_device_by_index(str_index)  # 打开设备
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
    def continuousAcquisition(self):
        # 触发方式为连续采集
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.textBrowser_tab1.append('开始采集图像')
        self.continuousAcquisitionStart()
    def continuousAcquisitionStart(self):
        self.cam.stream_on()
        self.acquisitionloop = True
        while self.acquisitionloop:
            try:
                # 从相机数据流中获取数据
                raw_image = self.cam.data_stream[0].get_image()
                if raw_image is None:
                    print("图像获取失败\n")
                    continue
                # 将原始图像数据转换为OpenCV格式
                self.numpy_image = raw_image.get_numpy_array()
                if self.numpy_image is None:
                    continue

                '''显示图像存在问题，其他都ok了'''
                # 将图像调整为与标签大小相同
                scaled_image = cv2.resize(self.numpy_image, (self.labelCamera1.width(), self.labelCamera1.height()))
                height, width= scaled_image.shape
                # 对于灰度图像，每行的字节数就等于图像的宽度（width），因为每个像素只有一个灰度值，不需要乘以通道数。
                bytes_per_line = width
                qt_image = QtGui.QImage(scaled_image.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_Grayscale8)
                # 在标签上显示图像
                self.labelCamera1.setPixmap(QtGui.QPixmap.fromImage(qt_image))
                # 让Qt程序有时间进行界面刷新
                QtWidgets.QApplication.processEvents()
            except KeyboardInterrupt:
                self.cam.stream_off()
                break
    def continuousAcquisitionStop(self):
        self.acquisitionloop = False  # 设置退出循环条件
        self.textBrowser_tab1.append('停止采集图像')

    def mode1_Start(self):
        # self.textBrowser_tab1.append('这是连续采集模式处理函数')
        # 如果
        if self.acquisitionloop is False:
            self.textBrowser_tab1.append("未获取到图像！\n")
            return
        # 如果没有获取图像，那么直接调取会报错,加入循环的话，运算量太大，导致程序崩溃
        # self.mode1loop = True
        # while self.mode1loop:
        #     image = self.numpy_image
        #     self.sortpeaks(image)
        image = self.numpy_image
        self.sortpeaks(image)

    def sortpeaks(self,image):
        # self.textBrowser_tab1.append('这是峰值处理函数')
        # 积分求平均并高斯滤波
        y = np.mean(image[400:801], axis=0)
        y = cv2.GaussianBlur(y ,(3,3) ,3)
        # 转置为行向量
        y = np.transpose(y)
        # 将二维数组转为一维数组
        y = y.ravel()

        # 画光谱图
        plt.figure(figsize=(4.27,3.41))
        plt.plot(y)
        # 获取绘制的图像，并转换为 QImage
        buf = io.BytesIO()
        plt.savefig(buf, format='png',dpi=100)
        plt.close()
        buf.seek(0)
        img = QtGui.QImage.fromData(buf.getvalue())

        # 将图像显示在 QLabel 中
        pixmap = QtGui.QPixmap.fromImage(img)
        self.labelSpectrum1.setPixmap(pixmap)

        # 找峰值
        peakloc, _ = find_peaks(y ,height=8 ,distance= 50)
        while len(peakloc) > 2:
            minValue = min(y[peakloc])
            minIndex = np.where(y[peakloc]==minValue)
            peakloc = np.delete(peakloc, minIndex)
        # 此时使用单峰算法
        if len(peakloc) < 2:
            self.textBrowser_tab1.append("此时只有一个水峰\n")
            return
        # 酒精峰，靠近405的那个(根据当前摆放在右侧)
        # 此时获取的是一个元素，而不是数值
        peak_a = y[peakloc[1]]
        # 水峰
        peak_w = y[peakloc[0]]
        if abs(peak_w) < 1e-10:  # 使用很小的阈值来判断 peak_w 是否接近于零
            self.textBrowser_tab1.append("警告：水峰的值接近于零，无法进行除法计算\n")
            self.lineEditPR_tab1_1.setText('存在错误')
            self.lineEditAC_tab1_1.setText('存在错误')
            return
        try:
            bizhi = peak_a / peak_w
            # 只保留后四位
            format_bizhi = "{:.4f}".format(bizhi)
            self.lineEditPR_tab1_1.setText(str(format_bizhi))
            self.textBrowser_tab1.append(f"峰值比:{format_bizhi}")
        except ZeroDivisionError:
            # 在这里处理捕获到的 ZeroDivisionError 异常,有备无患
            self.textBrowser_tab1.append("警告：水峰的值接近于零，无法进行除法计算\n")
            self.lineEditPR_tab1_1.setText('存在错误')
            self.lineEditAC_tab1_1.setText('存在错误')
            return
        # 根据bizhi进行计算,定义计算式
        def equation(x):
            return 0.4336*np.exp(0.0229*x)-bizhi
        solution = fsolve(equation,50.0)
        format_solution = "{:.2f}".format(solution[0])
        self.lineEditAC_tab1_1.setText(str(format_solution))
        self.textBrowser_tab1.append(f"峰值比:{format_solution}\n")

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