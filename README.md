# Gesture_Recognition
*本项目为**计算机视觉课程**的课程设计作业*

## 简介

通过RGB摄像头采集图像数据，并利用MediaPipe框架提取手部骨骼关键点信息。基于这些数据，系统识别并解析画面中的手部姿态。随后，根据预设的手势匹配规则，当用户摆出特定手势时，系统将触发相应的响应。此外，系统能够根据识别到的不同手势切换至不同的交互模式。

功能：
1. 手势调节计算机的屏幕亮度和媒体音量；
2. 手势模拟鼠标操作，包括光标的移动、点击及长按等动作；
3. 利用手势识别技术来识别汉语手指字母。


## 程序运行步骤
1. 确保`requirements.txt`中库已安装好
2. 在control.py所在目录下运行cmd或powershell窗口，执行`python .\control.py`命令。(测试可行)
3. 待弹出摄像头画面窗口，即可进行手势识别。

有关程序运行注意事项具体参考[程序运行说明](https://github.com/Nightingale-Bei/Gesture_Recognition/blob/main/%E7%A8%8B%E5%BA%8F%E8%BF%90%E8%A1%8C%E8%AF%B4%E6%98%8E.md)


## 原理
*具体实现原理及项目说明请参考[报告](https://github.com/Nightingale-Bei/Gesture_Recognition/blob/main/%E8%AF%B4%E6%98%8E.pdf)*

### MediaPipe
使用Mediapipe框架的[Hands](https://chuoling.github.io/mediapipe/solutions/hands.html)模块，其主要采集人手的骨骼关键点，包括各个手指的指骨关节以及每只手的腕关节的全部21个关键点，其中每个关键点都将输出3个值，分别为对应关键点的x、y、z。（z为深度信息，本项目没用到）

使用MediaPipe时，需要使用OpenCV读取视频文件并将视频帧作为输入传递给MediaPipe。MediaPipe会对每一帧图像进行监测，如果检测到手形或类似手型的目标，则会推测这些目标的骨骼关键点的坐标位置，并输出相关信息，其中包含左右手的label、每个关键点的label、序号和坐标信息。

![image](https://github.com/user-attachments/assets/d29d2a87-7457-4f70-8a18-2719595d3a74)



