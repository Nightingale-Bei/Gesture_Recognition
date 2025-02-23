import cv2
import HandDetectModule
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from BriVolControlModule import VolumeSetInit, BriVolumeSet
import HandGestureReco
import MouseModule

def cv2AddChineseText(img, text, position, textColor, textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def time_count(img, condition, time_set, text, circle_x, circle_y, circle_r, color1, color2, state):
    global time_init
    global time_counting
    global start_time
    if condition :
        if time_counting == False and time_init == False:
            time_init = True
        # 进入初始化时间
        if time_init:
            time_init = False
            time_counting = True
            start_time = time.time()
        if time_counting:
            encount_time = time.time() - start_time
            if encount_time > time_set*0.8:
                color = color1
            else:
                color = color2
            # 圆环绘制
            angle_start = 90
            angle_end = 360 + 90
            # angle = volper*1.2+30
            angle = np.interp(encount_time, [0, time_set], [angle_start, angle_end])
            cv2.ellipse(img, (circle_x, circle_y), (circle_r, circle_r), -180, angle_start, angle, color, 12)
            cv2.putText(img, text, (circle_x - 20, circle_y + 10), cv2.FONT_HERSHEY_PLAIN, 1.3, color, 2,)

            # 检查计时器是否已运行达到预设时间
            if (time.time() - start_time) >= time_set:
                return  1
            else: return 0
        else: return -1
    else:
        time_counting = False
        return -1



##############################

wCam, hCam = 960, 540   # 640, 360  /   1280, 720
frameR = 0
smoothening = 5
##############################
cap = cv2.VideoCapture(0)  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = HandDetectModule.HandDetector()
recognizer = HandGestureReco.GestureRecognizer()
mouse = MouseModule.GestureControlMouse(wCam, hCam, frame_region=80)


time_init = False
time_counting = False

Mode = 0
Mode_text = ' '
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img, handR, handL, handR_lmlist, handL_lmlist = detector.findHands(img, draw=False, hands_sep=True, flipType=False )  

    fingersUPR = [-1, -1, -1, -1, -1]
    fingersUPL = [-1, -1, -1, -1, -1]
    if handR or handL:
        if handL == True:
            fingersUPL = detector.fingersUp(handL_lmlist)
        if handR == True:
            fingersUPR = detector.fingersUp(handR_lmlist)


    hd = ""
    if handL == True and handR == False:
        hd = "L"
    elif handL == False and handR == True:
        hd = "R"
    elif handL == True and handR == True:
        hd = "L & R "
    else:
        hd = "None"
    cv2.putText(
        img, f"{str(hd)}", [
            125, 25], cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 255), 1
    )
    # 初始数据获得 完成
    
    # 主程序
    ##################################  
    if( handR or handL ) and not (fingersUPR == [1, 1, 1, 1, 1] and fingersUPL == [1, 1, 1, 1, 1]):
        if handL:
            if  Mode != 1 and fingersUPL == [0, 1, 0, 0, 0]:
                if(time_count(img, fingersUPL == [0, 1, 0, 0, 0], 3.0, "M_1", handL_lmlist[9][0], handL_lmlist[9][1], 30, (0, 255, 0), (0, 255, 255),1) == 1):
                    Mode = 1
                    Mode_text = '亮度音量控制'
                   
            elif Mode != 2 and fingersUPL == [0, 1, 1, 0, 0]:
                if(time_count(img, fingersUPL == [0, 1, 1, 0, 0], 3.0, "M_2",handL_lmlist[9][0], handL_lmlist[9][1], 30, (0, 255, 0), (0, 255, 255),2) == 1):
                    Mode = 2
                    Mode_text = '光标控制'
            
            elif Mode != 3 and fingersUPL == [0, 1, 1, 1, 0]:
                if(time_count(img, fingersUPL == [0, 1, 1, 1, 0], 3.0, "M_3",handL_lmlist[9][0], handL_lmlist[9][1], 30, (0, 255, 0), (0, 255, 255),2) == 1):
                    Mode = 3
                    Mode_text = '手语字母识别'
                    
            elif Mode != 0 and fingersUPL == [0, 0, 0, 0, 1]:
                if(time_count(img, fingersUPL == [0, 0, 0, 0, 1], 3.0, "M_0",handL_lmlist[9][0], handL_lmlist[9][1], 30, (0, 255, 0), (0, 255, 255),0) == 1):
                    Mode = 0
                    Mode_text = ' '
                    
            else :
                time_counting = False
                
        if handR == True:
            if Mode == 1 and (fingersUPR== [1,1,1,0,1] or fingersUPR== [1,1,0,1,1]):
                BriVolumeSet(img, handR, handL, handR_lmlist, handL_lmlist, fingersUPR, fingersUPL, VolumeSetInit(), draw=True)
            elif Mode == 2:
                mouse.control(img, fingersUPR, (handR_lmlist[8][0]+handR_lmlist[12][0]) // 2, (handR_lmlist[8][1]+handR_lmlist[12][1]) // 2, handR_lmlist)
            elif Mode == 3:
                recognized_gesture = recognizer.recognize_gesture(fingersUPR, handR_lmlist)
                recognizer.show_pic(img, recognized_gesture)
                cv2.putText(img, recognized_gesture, [15, 120], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    ##################################

    #* exit unit
    if handR and handL and fingersUPR == [1, 1, 1, 1, 1] and fingersUPL == [1, 1, 1, 1, 1]:
        if(time_count(img, 
                  fingersUPR == [1, 1, 1, 1, 1] and fingersUPL == [1, 1, 1, 1, 1], 
                  5.0, 
                  "Exit",
                  int((handL_lmlist[5][0] + handR_lmlist[5][0]) / 2.0), 
                  int((handL_lmlist[5][1] + handR_lmlist[5][1]) / 2.0), 
                  50,
                  (0, 0, 255),
                  (0, 255, 255),
                  -1
                  ) == 1):
            break

  

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"fps:{int(fps)}", [15, 25], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.putText(img, f"Mode:{Mode}", [15, 55], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    img = cv2AddChineseText(img, Mode_text, (15, 65),(255, 0, 255), 30)
    cv2.imshow("Image", img)
    cv2.waitKey(1)


print("Exit!!!!!!!!")

