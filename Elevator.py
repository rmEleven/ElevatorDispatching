from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import time
from functools import partial

class Elevator(QThread):
    '''
    创建一个名为Elevator的类，继承QThread类
    '''

    trigger = pyqtSignal(int)  # 实例化一个信号对象

    def __init__(self, id, mainWindow):
        '''构造函数'''
        super().__init__()                # 调用父类QThread的构造函数
        self.trigger.connect(self.check)  # 将信号trigger连接到check函数

        self.id = id                  # 电梯编号id
        self.mainWindow = mainWindow  # 电梯图形化界面

        self.arrive = 0         # 电梯是否到达目标楼层
        self.pause = 0          # 电梯是否暂停运行
        self.state = 0          # 电梯状态 0:停止 1:向上运行 -1:向下运行
        self.floor = 1          # 电梯当前所在楼层
        self.target = set([])   # 电梯的目标楼层集合

    def run(self):
        '''重写QThread的run方法'''
        while (1):
            if self.arrive == 1:  # 电梯到达目标楼层
                # 设置按钮的样式为开门图片
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.id)).setStyleSheet("QPushButton{background-image: url(open.png)}")
                time.sleep(3)  # 线程休眠3秒
                # 将按钮的样式设置为空
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.id)).setStyleSheet("QPushButton{}")
                self.arrive = 0  # 将arrive设置为0
            
            self.trigger.emit(self.id)  # 发射信号trigger，并传递参数self.id
            time.sleep(1)               # 线程休眠1秒
    
    def check(self):
        if self.pause == 0:  # 电梯没有暂停运行
            
            '''改变电梯楼层'''
            #if (self.floor in self.target) or (self.floor in self.mainWindow.up) or (self.floor in self.mainWindow.down):
            if self.state == 1:              # 电梯处于向上状态
                self.floor = self.floor + 1  # 向上移动一层
            elif self.state == -1:           # 电梯处于向下状态
                self.floor = self.floor - 1  # 向下移动一层
            self.mainWindow.findChild(QLCDNumber, "{0}".format(self.id)).display(self.floor)  # 显示电梯楼层
            
            '''电梯处于向上状态'''
            if self.state == 1:
                self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉电梯内部该层的标识
                self.mainWindow.findChild(QPushButton, "up{0}".format(self.floor)).setStyleSheet("QPushButton{}")             # 去掉电梯外部该层的标识
                if (self.floor in self.target) or (self.floor in self.mainWindow.up):  # 到达目标楼层
                    self.arrive = 1
                self.target.discard(self.floor)         # 从目标楼层集合中移除该层
                self.mainWindow.up.discard(self.floor)  # 从楼层等待集合中移除该层

                if len(list(self.target)) == 0:  # 电梯要到达的目标楼层集合为空
                    self.state = 0               # 电梯已经没有任务，状态置为0，表示电梯静止等待。
                # 如果电梯要到达的目标楼层列表不为空，且列表中最大的目标楼层小于当前楼层，说明电梯应该向下运动，状态置为-1，表示电梯正在向上运动。
                if (len(list(self.target)) != 0) and (max(list(self.target)) < self.floor):
                    self.state = -1

            '''电梯处于向下状态'''
            if self.state == -1:
                self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉电梯内部该层的标识
                self.mainWindow.findChild(QPushButton, "down{0}".format(self.floor)).setStyleSheet("QPushButton{}")           # 去掉电梯外部该层的标识
                if (self.floor in self.target) or (self.floor in self.mainWindow.down):  # 到达目标楼层
                    self.arrive = 1
                self.target.discard(self.floor)           # 从目标楼层集合中移除该层
                self.mainWindow.down.discard(self.floor)  # 从楼层等待集合中移除该层

                if len(list(self.target)) == 0:  # 电梯要到达的目标楼层集合为空
                    self.state = 0               # 电梯已经没有任务，状态置为0，表示电梯静止等待。
                # 如果电梯要到达的目标楼层列表不为空，且列表中最小的目标楼层大于当前楼层，说明电梯应该向上运动，状态置为1，表示电梯正在向上运动。
                if (len(list(self.target)) != 0) and (min(list(self.target)) > self.floor):
                    self.state = 1

            '''电梯处于静止状态'''            
            if self.state == 0:
                # 如果电梯内有要到达的楼层并且电梯内的目标楼层最大值大于当前电梯所在的楼层
                if (len(list(self.target)) != 0) and (max(list(self.target)) > self.floor):
                    self.state = 1  # 向上运动
                # 如果电梯内有要到达的楼层并且电梯内的目标楼层最小值小于当前电梯所在的楼层
                if (len(list(self.target)) != 0) and (min(list(self.target)) < self.floor):
                    self.state = -1  # 向下运动
        
    def pause(self):
        if self.pause == 0:  # 如果该电梯未被暂停
            self.pause = 1  # 将该电梯的暂停状态设为已暂停
            self.mainWindow.findChild(QPushButton, "pause{0}".format(self.id)).setText("暂停")  # 将该电梯对应的暂停按钮文本设置为“暂停”
        else:  # 如果该电梯已被暂停
            self.pause = 0  # 将该电梯的暂停状态设为未暂停
            self.mainWindow.findChild(QPushButton, "pause{0}".format(self.id)).setText("启动")  # 将该电梯对应的暂停按钮文本设置为“启动”

    def add_target(self, floor):
        '''将楼层添加到电梯的目标楼层集合中'''
        # 找到对应的按钮，并设置样式为背景图片为background.png
        self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, floor)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        # 将目标楼层添加到对应电梯的目标楼层集合中
        self.target.add(floor)