import cv2
import HandDetectModule as htm
import autopy
import numpy as np
import time
import math
import subprocess

class GestureControlMouse:
    def __init__(self, width=1280, height=720, frame_region=80, smoothening=3):
        self.ispress = False
        self.keyboard = False
        
        #一个坐标点中含有1.25个像素点。
        # self.wCam, self.hCam = int(width/1.25), int(height/1.25)
        self.wCam, self.hCam = width ,height
        self.frameR = frame_region
        self.smoothening = smoothening
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.wScr, self.hScr = autopy.screen.size()  # Get screen size
    
    def distance(self, point1, point2, handR_lmlist):
        dis_get = math.hypot(point1, point2)
        dis_base = math.hypot(handR_lmlist[5][0]-handR_lmlist[17][0], handR_lmlist[5][1]-handR_lmlist[17][1])
        return dis_get / dis_base

    def control(self, img, fingerUP, x, y, handR_lmlist):
            # 食指&中指up，操作鼠标
            if fingerUP[1:5] == [1,1,0,0] :  
                if self.keyboard == False:
                    self.process = subprocess.Popen('key_software\\FreeVK.exe')
                    self.keyboard = True
                    print("FreeVK.exe已打开")
                cv2.rectangle(img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR), (0, 255, 0), 2)
                dis = self.distance(handR_lmlist[12][0]-handR_lmlist[8][0],handR_lmlist[12][1]-handR_lmlist[8][1],handR_lmlist)
                if dis < 0.4 and self.ispress == False:
                    autopy.mouse.toggle(None,True)
                    self.ispress = True
                elif dis > 0.9 and self.ispress == True:
                    self.ispress = False
                    autopy.mouse.toggle(None,False)
                if self.ispress == True:
                    cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)
                self.plocX, self.plocY = self.clocX, self.clocY
                x3 = np.interp(x, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
                y3 = np.interp(y, (self.frameR, self.hCam - self.frameR), (0, self.hScr))
                self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening
                autopy.mouse.move(self.clocX, self.clocY)

            # 复位、释放，避免bug
            elif self.ispress == True:
                self.ispress = False
                autopy.mouse.toggle(None,False)
            elif self.keyboard == True:
                self.process.terminate()
                self.process.wait()
                self.keyboard = False
                print("FreeVK.exe已关闭")
            
            

            

              





if __name__ == "__main__":  
    wCam, hCam = 640, 360
    frameR = 100
    smoothening = 5
    cap = cv2.VideoCapture(0)  
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    detector = htm.HandDetector()
    mouse = GestureControlMouse(width=wCam, height=hCam)
    wScr, hScr = autopy.screen.size()
    # print(wScr, hScr)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img, handR, handL, handR_lmlist, handL_lmlist = detector.findHands(img, draw=False, hands_sep=True, flipType=False) 

        fingersUPR = [-1, -1, -1, -1, -1]
        fingersUPL = [-1, -1, -1, -1, -1]
        if handR or handL:
            if handL == True:
                fingersUPL = detector.fingersUp(handL_lmlist)
            if handR == True:
                fingersUPR = detector.fingersUp(handR_lmlist)


        ####################

        if handR:
            mouse.control(img, fingersUPR, (handR_lmlist[8][0]+handR_lmlist[12][0]) // 2, (handR_lmlist[8][1]+handR_lmlist[12][1]) // 2, handR_lmlist)

        ####################

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{int(fps)}', [15, 25], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)