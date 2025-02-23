"""
Reference from cvzone.HandTrackingModule

"""
import math
import cv2
import mediapipe as mp
import numpy as np
import time

class HandDetector:
    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.8, minTrackCon=0.8):

        self.staticMode = staticMode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.staticMode,
                                        max_num_hands=self.maxHands,
                                        model_complexity=modelComplexity,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)

        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True, hands_sep=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        handR = False
        handL = False
        handL_lmlist = []
        handR_lmlist = []
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                mylmList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    mylmList.append([px, py])
                myHand["lmList"] = mylmList


                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        if hands_sep == True :
            if len(allHands) == 1:
                if allHands[0]["type"] == "Right" :
                    handR = True
                    handR_lmlist = allHands[0]["lmList"]
                elif allHands[0]["type"] == "Left" :
                    handL = True
                    handL_lmlist = allHands[0]["lmList"]
            elif len(allHands) == 2 :
                handR = True
                handL = True
                if allHands[0]["type"] == "Left":
                    handL_lmlist = allHands[0]["lmList"]
                    handR_lmlist = allHands[1]["lmList"]
                else :
                    handL_lmlist = allHands[1]["lmList"]
                    handR_lmlist = allHands[0]["lmList"]
            return img, handR, handL, handR_lmlist, handL_lmlist
        elif hands_sep == False :
            return  img, allHands
        

    def fingersUp(self, Hand):

        fingers = []
        LmList = Hand
        if self.results.multi_hand_landmarks:
            # 拇指弯曲判断 向量夹角角度(1-2)&(2-3)

            A = (LmList[1][0]-LmList[2][0])*(LmList[3][0]-LmList[2][0])+(LmList[1][1]-LmList[2][1])*(LmList[3][1]-LmList[2][1])
            B = math.sqrt(math.pow(LmList[1][0]-LmList[2][0],2)+math.pow(LmList[1][1]-LmList[2][1],2))*math.sqrt(math.pow(LmList[3][0]-LmList[2][0],2)+math.pow(LmList[3][1]-LmList[2][1],2))
            if  A/B < -1.0:
                ratio = -1.0
            elif A/B > 1.0:
                ratio = 1.0
            else: ratio = A/B
            sita = math.acos(ratio)/math.pi*180.0
            if sita > 153.0:
                fingers.append(1)
            elif sita < 153.0:
                fingers.append(0)
            # 其余手指
            for id in range(1, 5):
                if math.hypot(LmList[self.tipIds[id]][0] - LmList[0][0], LmList[self.tipIds[id]][1] - LmList[0][1]) > math.hypot(LmList[self.tipIds[id] - 2][0] - LmList[0][0], LmList[self.tipIds[id] - 2][1] - LmList[0][1]):
                    fingers.append(1)
                else:
                    fingers.append(0)

        return fingers

    # 自定义距离信息测试
    def hand_cam_distance(self, img, Hand, draw):
        dis = -1.0
        LmList = Hand
        if self.results.multi_hand_landmarks:    
            dis = math.hypot(LmList[5][0] - LmList[17][0], LmList[5][1] - LmList[17][1])
            # print('Distance:', dis)
            dis = 2852.3 * pow(dis, -0.932)
            cv2.putText(img, 'Dis:' + str(int(dis)), (10, 110), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            if dis < 35.0 and dis > 15.0:
                # 透明度图叠加
                blk = np.zeros(img.shape, np.uint8)
                cv2.rectangle(blk, (LmList[5][0] - 20, LmList[5][1] - 20), (LmList[5][0] + 30, LmList[5][1] + 30), (250, 0, 250), cv2.FILLED)
                img = cv2.addWeighted(img, 1.0, blk, 0.9, 1)
        return img, dis


    def hand_alpha(self, img, LmList ,draw_text=True, draw_circle = False):    
        # if self.results.multi_hand_landmarks:
            # 角度测试
        alpha = math.atan2( LmList[17][1] - LmList[5][1], LmList[17][0] - LmList[5][0])
        alpha = alpha / math.pi * 180.0
        # print('Alpha:', alpha)
        if draw_text:
            cv2.putText(img, 'Alpha:' + str(int(alpha)), (10, 140), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
            
            # if draw_circle:
            # # 圆环绘制
            #     circle_x = int( (LmList[0][1] + LmList[5][1] + LmList[17][1]) / 3.0)
            #     circle_y = int( (LmList[0][2] + LmList[5][2] + LmList[17][2]) / 3.0)
            #     circle_r = 100
            #     cv2.ellipse(img, (circle_x, circle_y), (circle_r, circle_r), -180, 0, alpha, (0, 0, 255), 12)
            #     circle_r = circle_r + 7
            #     cv2.ellipse(img, (circle_x, circle_y), (circle_r, circle_r), -180, 0, 180, (0, 0, 255), 3)
            #     circle_r = circle_r - 14 
            #     cv2.ellipse(img, (circle_x, circle_y), (circle_r, circle_r), -180, 0, 180, (0, 0, 255), 3)
        else:    
            alpha = -181
        return alpha


def main():
    wCam, hCam = 640, 360
    frameR = 0
    smoothening = 5
    cap = cv2.VideoCapture(0)  
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0
    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        img, handR, handL, handR_lmlist, handL_lmlist = detector.findHands(img, draw=True, hands_sep=True, flipType=False )  
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
            hd = "[None]"
        cv2.putText(img, f"{str(hd)}", [125, 25], cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 255), 1)
        ################
        # debug block

        ################

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"fps:{int(fps)}", [15, 25], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)

        cv2.waitKey(1)


if __name__ == "__main__":
    main()
