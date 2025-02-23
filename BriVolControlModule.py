""" 
亮度音量控制模块

"""

import cv2
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from HandDetectModule import HandDetector
import BriVolControlModule as volctrl
import screen_brightness_control as sbc
import wmi


def VolumeSetInit():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volumeRange = volume.GetVolumeRange()  # (-63.5, 0.0, 0.03125)
    minvol = volumeRange[0]
    maxvol = volumeRange[1]
    return volume

  
def hand_alpha(img, LmList ,draw_text=True, draw_circle = False):   

    alpha = math.atan2( LmList[17][1] - LmList[5][1], LmList[17][0] - LmList[5][0])
    alpha = alpha / math.pi * 180.0
    # print('Alpha:', alpha)
    if draw_text:
        cv2.putText(img, 'Alpha:' + str(int(alpha)), (10, 140), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
        

    return alpha

def BriVolumeSet(
    img,
    handR,
    handL,
    handR_lmlist,
    handL_lmlist,
    fingersUPR,
    fingersUPL,
    volume,
    draw=True,
):
    handR_lmlist = handR_lmlist
    alpha = hand_alpha(img,handR_lmlist,draw_text=False)
   
    if fingersUPR == [1, 1, 1, 0, 1] or fingersUPR == [1, 1, 0, 1, 1]:
        mode = ' '
        color = (255, 255, 0)
        if fingersUPR == [1, 1, 1, 0, 1]:
            volper = np.interp(alpha, [-40, 80], [0, 100], 0, 100)
            vol_value = volper / 100
            volume.SetMasterVolumeLevelScalar(vol_value, None)
            number = volper
            color = (219, 219, 44)
            mode = 'Vol:'
     
        elif fingersUPR == [1, 1, 0, 1, 1]:
            brightness = np.interp(alpha, [-40, 80], [0, 100], 0, 100)
            # print(f"{alpha}\t\t{brightness}")
              # 创建WMI客户端
            c = wmi.WMI(namespace='root\\wmi')
            # 获取WmiMonitorBrightnessMethods对象
            monitor = c.WmiMonitorBrightnessMethods()[0]
            # 设置亮度，其中brightness参数为0-100之间的整数
            monitor.WmiSetBrightness(int(brightness), True)
            number = brightness
            color = (100, 230, 60)
            mode = 'Bri:'
        else: number = 0
        # 圆环绘制
        circle_x = int(
            (handR_lmlist[0][0] + handR_lmlist[5][0] + handR_lmlist[17][0])
            / 3.0
        )
        circle_y = int(
            (handR_lmlist[0][1] + handR_lmlist[5][1] + handR_lmlist[17][1])
            / 3.0
        )
        circle_r = 100
        angle_start = 30
        angle_end = 150

        angle = np.interp(number, [0, 100], [30, 150])
        if angle < angle_start:
            angle = angle_start
        elif angle > angle_end:
            angle = angle_end
        cv2.ellipse(
            img,
            (circle_x, circle_y),
            (circle_r, circle_r),
            -180,
            angle_start,
            angle,
            color,
            12,
        )
        circle_r = circle_r + 7
        cv2.ellipse(
            img,
            (circle_x, circle_y),
            (circle_r, circle_r),
            -180,
            angle_start,
            angle_end,
            color,
            2,
        )
        circle_r = circle_r - 14
        cv2.ellipse(
            img,
            (circle_x, circle_y),
            (circle_r, circle_r),
            -180,
            angle_start,
            angle_end,
            color,
            2,
        )

        # 画数值
        cv2.putText(
            img,
            f"{mode}{int(number)}%",
            (circle_x-10, circle_y),
            cv2.FONT_HERSHEY_PLAIN,
            2,
            color,
            2,
        )
