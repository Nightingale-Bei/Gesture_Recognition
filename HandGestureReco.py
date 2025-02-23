import cv2
import HandDetectModule
import time
import numpy as np
import math

class GestureRecognizer:
    def __init__(self):
        # 创建映射，键为整数列表
        self.gestures = {
            (1, 0, 0, 0, 0): ["A", "C", "O", "Q" ,"SH","S"],
            (0, 1, 1, 1, 1): "B",
            (0, 0, 0, 0, 0): ["D", "M", "N"],
            (0, 0, 1, 1, 1): "E",
            (0, 1, 0, 0, 0): ["G", "I", "J"],
            (0, 1, 1, 0, 0): ["F","H", "V", "X"],
            (1, 1, 1, 0, 0): "K",       # 抬高手腕   或1 1 0 0 0  
            (1, 1, 0, 0, 0): ["L","R"],
            (0, 1, 0, 0, 1): ["T", "Z"],
            (0, 1, 1, 0, 1): "ZH",  
            (1, 1, 1, 1, 1): ["P", "CH", "U"],
            (1, 0, 0, 0, 1): "Y",
            (0, 1, 1, 1, 0): "W",
            (0, 0, 0, 0, 1): "NG"   
        }

    def recognize_gesture(self, data, handRlmlist):
        # 将输入数据转换为映射中的键格式
        key = tuple(data)
        # 查找并返回对应的手势字母
        possible_letters = self.gestures.get(key)
        if possible_letters:
            if len(possible_letters) > 1:
                # 如果有多个可能的字母，进行二次判断
                if possible_letters =='NG':
                    return possible_letters
                elif possible_letters =="ZH":
                    return possible_letters
                else:
                    return self.secondary_recognition(key,handRlmlist)
            else:
                return possible_letters
        else:
            return "NONE"
    
    def finger_distance(self, point1, point2, handR_lmlist):
        dis_get = math.hypot(point1, point2)
        dis_base = math.hypot(handR_lmlist[5][0]-handR_lmlist[17][0], handR_lmlist[5][1]-handR_lmlist[17][1])
        return dis_get / dis_base
    
    def finger_alpha(self, point1, point2):
        alpha = math.atan2(-point1, -point2)
        alpha = alpha / math.pi * 180.0
        return round(alpha,2)

    def secondary_recognition(self, key, handR_lmlist):
        possible_letter = "None"
        # A_Group
        if key == (1, 0, 0, 0, 0):
            dis_thumb_index = self.finger_distance(handR_lmlist[4][0]-handR_lmlist[8][0],handR_lmlist[4][1]-handR_lmlist[8][1],handR_lmlist)
            dis_mid_ring = self.finger_distance(handR_lmlist[12][0]-handR_lmlist[16][0], handR_lmlist[12][1]-handR_lmlist[16][1], handR_lmlist)
            if  dis_mid_ring < 0.45:    # 中指 - 无名指 指尖距离
                if dis_thumb_index < 0.35 : # 拇指 - 食指 指尖距离
                    possible_letter = 'O'
                elif dis_thumb_index > 0.4 and dis_thumb_index < 0.9 : # 拇指 - 食指 指尖距离
                    possible_letter = 'C'
                elif dis_thumb_index > 1.0 : # 拇指 - 食指 指尖距离
                    alpha_direction = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
                    if alpha_direction > -40 and alpha_direction < 30 :
                        possible_letter = 'S'
                    else:
                        possible_letter = 'A' 
            elif dis_mid_ring > 0.6:
                if  dis_thumb_index < 0.35 : # 拇指 - 食指 指尖距离
                    possible_letter = 'Q'
                elif dis_thumb_index > 0.4 :
                    possible_letter = 'SH'

        # ["D", "M", "N"]
        if key == (0, 0, 0, 0, 0):
            if self.finger_distance(handR_lmlist[20][0]-handR_lmlist[16][0],handR_lmlist[20][1]-handR_lmlist[16][1], handR_lmlist) > 0.3 :   # 无名指 - 小指 指尖距离
                possible_letter = 'M'
            elif self.finger_distance(handR_lmlist[12][0]-handR_lmlist[16][0],handR_lmlist[12][1]-handR_lmlist[16][1], handR_lmlist ) > 0.3 :     # 中指 - 无名指 指尖距离
                possible_letter = 'N'
            else:
                possible_letter = 'D'

        # ["G", "I", "J"]
        if key == (0, 1, 0, 0, 0):
            alpha1= self.finger_alpha(handR_lmlist[6][0]-handR_lmlist[5][0],handR_lmlist[6][1]-handR_lmlist[5][1])-90
            alpha2=self.finger_alpha(handR_lmlist[7][0]-handR_lmlist[6][0],handR_lmlist[7][1]-handR_lmlist[6][1])-90
            alpha_dif = alpha1 -alpha2
            # print(f"{alpha1:.2f}\t{alpha2:.2f}\t{alpha_dif:.2f}")
            if alpha_dif >28:
                possible_letter = 'J'
            elif alpha_dif > 0 and alpha_dif <10 :
                alpha_direction = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
                if alpha_direction > -40 and alpha_direction < 30 :
                    possible_letter = 'I'
                else:
                    possible_letter = 'G' 
        # ["L","R"]
        if key == (1, 1, 0, 0, 0): 
            alpha_direction = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
            if alpha_direction > -40 and alpha_direction < 30 :
                possible_letter = 'L'
            else:
                possible_letter = 'R'


        # ["F","H", "V", "X"]
        if key == (0, 1, 1, 0, 0):
            alpha_index = self.finger_alpha(handR_lmlist[8][0]-handR_lmlist[5][0],handR_lmlist[8][1]-handR_lmlist[5][1])
            alpha_middle = self.finger_alpha(handR_lmlist[12][0]-handR_lmlist[5][0],handR_lmlist[12][1]-handR_lmlist[5][1])
            alpha = alpha_index - alpha_middle
            if alpha < 4:
                possible_letter = 'X'
            elif alpha < 22 and alpha >7 :
                possible_letter = 'H'
            elif alpha > 30:
                alpha_direction = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
                if alpha_direction > -40 and alpha_direction < 30 :
                    possible_letter = 'V'
                else:
                    possible_letter = 'F'

        # ["T", "Z"]
        # 根据手的朝向判断
        # -40~30  T
        # 240~ 270  -90~-80  Z
        if key == (0, 1, 0, 0, 1):
            alpha = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
            if alpha > -40 and alpha < 30 :
                possible_letter = 'T'
            else:
                possible_letter = 'Z'
        
        #  ["P", "CH","U"],
        if key == (1, 1, 1, 1, 1):
            dis_thumb_index = self.finger_distance(handR_lmlist[4][0]-handR_lmlist[8][0],handR_lmlist[4][1]-handR_lmlist[8][1], handR_lmlist) 
            if dis_thumb_index < 0.3:  
                possible_letter = 'P'
            elif dis_thumb_index > 0.5 and dis_thumb_index < 1.2:
                possible_letter = 'CH'
            elif dis_thumb_index > 1.3 :
                possible_letter = 'U'
            # print(dis_thumb_index)
        

        return possible_letter

    def show_pic(self, img, letter, is_show = True):
        img_path_dic = {
        "A": "image/A.png",
        "B": "image/B.png",
        "C": "image/C.png",
        "D": "image/D.png",
        "E": "image/E.png",
        "F": "image/F.png",
        "G": "image/G.png",
        "H": "image/H.png",
        "I": "image/I.png",
        "J": "image/J.png",
        "K": "image/K.png",
        "L": "image/L.png",
        "M": "image/M.png",
        "N": "image/N.png",
        "O": "image/O.png",
        "P": "image/P.png",
        "Q": "image/Q.png",
        "R": "image/R.png",
        "S": "image/S.png",
        "T": "image/T.png",
        "U": "image/U.png",
        "V": "image/V.png",
        "W": "image/W.png",
        "X": "image/X.png",
        "Y": "image/Y.png",
        "Z": "image/Z.png",
        "ZH": "image/ZH.png",
        "CH": "image/CH.png",
        "SH": "image/SH.png",
        "NG": "image/NG.png"
    }
        if is_show:
            if not (letter == 'None' or letter == 'NONE'):
                img_path = img_path_dic.get(letter)
                overlay_img=cv2.imread(img_path)

                # 确定叠加位置
                x_offset = 0
                y_offset = img.shape[0] - overlay_img.shape[0]
                # 制作小图片的掩膜并取反
                overlay_gray = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(overlay_gray, 10, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)

                # 应用掩膜，只保留小图片中非透明部分的像素
                img1_bg = cv2.bitwise_and(img[y_offset:y_offset+overlay_img.shape[0], x_offset:x_offset+overlay_img.shape[1]], img[y_offset:y_offset+overlay_img.shape[0], x_offset:x_offset+overlay_img.shape[1]], mask=mask_inv)
                img2_fg = cv2.bitwise_and(overlay_img, overlay_img, mask=mask)

                # 将小图片叠加到画面上
                dst = cv2.add(img1_bg, img2_fg)
                img[y_offset:y_offset+overlay_img.shape[0], x_offset:x_offset+overlay_img.shape[1]] = dst

        
if __name__ == "__main__":
    wCam, hCam = 640, 360
    frameR = 0
    smoothening = 5
    cap = cv2.VideoCapture(0)  
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0

    recognizer = GestureRecognizer()
    detector = HandDetectModule.HandDetector()

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
        #################################################
        
        # 示例使用

        recognized_gesture = recognizer.recognize_gesture(fingersUPR, handR_lmlist)
        recognizer.show_pic(img, recognized_gesture)
        cv2.putText(img, recognized_gesture, [15, 105], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        

        ##############################################
        if handR:
            # dis_thumb_index = recognizer.finger_distance(handR_lmlist[4][0]-handR_lmlist[8][0],handR_lmlist[4][1]-handR_lmlist[8][1])
            # dis_mid_ring = recognizer.finger_distance(handR_lmlist[12][0]-handR_lmlist[16][0],handR_lmlist[12][1]-handR_lmlist[16][1])

            # print(f"{dis_thumb_index:.2f}\t{dis_mid_ring:.2f}")

            cv2.putText( img, f"R:{str(fingersUPR)}", [125, 65], cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 255), 1 )
        #     alpha_index = self.finger_alpha(handR_lmlist[17][0]-handR_lmlist[5][0],handR_lmlist[17][1]-handR_lmlist[5][1])+90
        #     print(alpha_index)
            
        ##########################
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"fps:{int(fps)}", [15, 25], cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)