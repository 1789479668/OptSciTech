import cv2
import scipy.signal

import gxipy as gx
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import DetectorWindow

def testfuc():
    print('成功效用该函数')
# 输出一个图片的numpy数组
def sortpeaks(image):
    # 积分求平均并高斯滤波
    y = np.mean(image[400:801], axis=0)
    y = cv2.GaussianBlur(y ,(3,3) ,3)
    # 转置为行向量
    y = np.transpose(y)
    y = y.ravel()

    # 找峰值
    peakloc, _ = scipy.signal.find_peaks(y ,height=8 ,distance= 50)
    if len(peakloc) < 2:
        print('只有一个水峰')

    while len(peakloc) > 2:
        minValue = min(y[peakloc])
        minIndex = np.where(y[peakloc]==minValue)
        peakloc = np.delete(peakloc, minIndex)

    # 酒精峰，靠近405的那个(根据当前摆放在右侧)
    # 此时获取的是一个元素，而不是数值
    peak_a = y[peakloc[1]]
    # 水峰
    peak_w = y[peakloc[0]]

    # plt.plot(y)
    # plt.show()


    bizhi = peak_a / peak_w

    # # 获取精确解，运行速度太慢了
    # x = sp.Symbol('x')
    # y = 0.4336*sp.exp(0.0229*x)
    # solutions = sp.solve(y-bizhi, x)
    #
    # for solution in solutions:
    #     print(f"x = {solution}")
    # return solutions
    def equation(x):
        return 0.4336*np.exp(0.0229*x)-bizhi
    solutions = scipy.optimize.fsolve(equation,50.0)
    return solutions

def getimage(*args):
    # 输出获取图片的初始化信息
    print("")
    print("-------------------------------------------------------------")
    print("正在调用相机获取图像信息")
    print("-------------------------------------------------------------")
    print("")
    print("初始化中......")
    print("")

    # 创建设备管理器
    device_manager = gx.DeviceManager()
    # 更新设备列表
    dev_num, dev_info_list = device_manager.update_device_list()
    print(f"当前可用设备数量:{dev_num}\n")
    if dev_num == 0:
        print("没有找到相机设备。\n")
        return

    # 获取设备基本信息列表
    str_index = dev_info_list[0].get("index")

    # 打开设备
    cam = device_manager.open_device_by_index(str_index)

    # 触发方式为连续采集
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

    # 设置曝光时间（默认1s，100000us）
    cam.ExposureTime.set(10000)

    # 设置增益(默认为0，可调为0~16dB)
    cam.Gain.set(0)

    # 初始化参数完毕
    print("初始化参数完毕,即将开始获取图片\n")

    # 开始图像采集流
    cam.stream_on()

    try:
        while True:
            # 从相机数据流中获取数据
            raw_image = cam.data_stream[0].get_image()
            if raw_image is None:
                print("图像获取失败\n")
                continue

            # 将原始图像数据转换为OpenCV格式
            numpy_image = raw_image.get_numpy_array()
            if numpy_image is None:
                continue

            # # 展示实时图像(不去显示，否则耗时耗时太多会丢帧)
            cv2.imshow("实时图像", numpy_image)
            # 按下'q'键退出循环
            # solutions = sortpeaks(numpy_image)
            # print(f'x={solutions}')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # 停止图像数据流采集
        cam.stream_off()

        #关闭设备
        cam.close_device()
        print("-------------------------------------------------------------")
        print("结束图像获取，且关闭相机完毕")
        print("-------------------------------------------------------------")
        cv2.destroyAllWindows()