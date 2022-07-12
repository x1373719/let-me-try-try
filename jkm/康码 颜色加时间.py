import cv2
from pyzbar import pyzbar
import requests
import urllib.request
import time
import numpy as np

# 颜色范围定义
color_dist = {
    'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
    'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
}

# 检测颜色
def detect_color(image, color):
    gs = cv2.GaussianBlur(image, (5, 5), 0)  # 高斯模糊
    hsv = cv2.cvtColor(gs, cv2.COLOR_BGR2HSV)  # HSV
    inRange_hsv = cv2.inRange(hsv, color_dist[color]['Lower'], color_dist[color]['Upper']) #返回mask
    image_s = image.shape[0]*image.shape[1] #图片面积
    ratio = sum(sum(inRange_hsv//255))/image_s
    if ratio > 0.1 :
        return True
    else:
        return False


def time_to_str(time_1):
    """
    时间戳转化为字符串
    :param time_1:输入的时间戳
    :return: str_1:输出的字符串 默认格式 "Y_m_d-H_M_S" 统一格式
    """
    time_2 = time.localtime(time_1) #转化成时间结构
    str_1 = time.strftime("%Y_%m_%d-%H_%M_%S", time_2)
    return str_1



def get_result(image):
    QR_code_all = pyzbar.decode(image)
    reslut = '目标中没有二维码'
    if QR_code_all != []:
        time_QR = '无法确定'
        try:
            QR_code_date = QR_code_all[0].data.decode('utf-8')
            QR_code_rect = QR_code_all[0].rect
            try:
                QR_code_time = int(QR_code_date[-13:-3])
                now_time = int(time.time())#当前时间
                if now_time-QR_code_time > 120: #大于30秒
                    reslut = '二维码过期'
                    return reslut
                time_QR = time_to_str(QR_code_time)
            except:
                pass

            x_1 = QR_code_rect.left
            y_1 = QR_code_rect.top
            x_2 = QR_code_rect.width + x_1
            y_2 = QR_code_rect.height + y_1
            #得到两点坐标
            image_rect = image[y_1:y_2,x_1:x_2].copy()
            is_green = detect_color(image_rect,'green') #判断是否为绿色
            if is_green:
                reslut = '>>>绿码<<<时间:'+time_QR
                return reslut
            else:
                reslut = '>>>非绿码<<<时间:' + time_QR
                return reslut
        except Exception as e:
            return reslut
    else:
        return reslut


if __name__ == '__main__':
    while True:
        try:
            video_reader = cv2.VideoCapture(0)  # 读取视频
            if video_reader.isOpened():
                print('成功打开摄像头')
                while True:
                    _, image = video_reader.read()
                    result = get_result(image)
                    print(result)
                    time.sleep(0.2)
            else:
                print('无法打开摄像头')
                time.sleep(1)
        except Exception as e:
            video_reader.release()
            print('重启程序')
