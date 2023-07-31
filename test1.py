import cv2
import scipy.signal

import gxipy as gx
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def getimage():
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

            # 展示实时图像(不去显示，否则耗时耗时太多会丢帧)
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

getimage()