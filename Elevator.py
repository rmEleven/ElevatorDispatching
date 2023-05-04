from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time


class Elevator(QThread):
    '''创建一个名为Elevator的类模拟电梯，继承QThread类'''

    trigger = pyqtSignal(int)  # 实例化一个信号对象

    def __init__(self, id, mainWindow):
        '''构造函数'''
        super().__init__()                # 调用父类QThread的构造函数
        self.trigger.connect(self.check)  # 将信号trigger连接到check函数

        self.id = id                      # 电梯编号id
        self.mainWindow = mainWindow      # 电梯图形化界面

        self.arrive = 0                   # 电梯是否到达目标楼层
        self.error = 0                    # 电梯是否出现故障
        self.state = 0                    # 电梯状态 0:停止 1:向上运行 -1:向下运行
        self.floor = 1                    # 电梯当前所在楼层
        self.target = set([])             # 电梯的目标楼层集合

    def run(self):
        '''重写QThread的run方法'''
        while (1):
            if self.arrive == 1:  # 电梯到达目标楼层
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.id)).setStyleSheet("QPushButton{background-image: url(open.png)}")  # 设置按钮的样式为开门图片
                time.sleep(3)     # 线程休眠3秒
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.id)).setStyleSheet("QPushButton{}")  # 将按钮的样式设置为空
                self.arrive = 0   # 将arrive设置为0
            
            self.trigger.emit(self.id)  # 发射trigger信号 调用check函数
            time.sleep(1)               # 线程休眠1秒
    
    def check(self):
        '''检查电梯是否到达目标楼层并调整其状态'''

        '''故障电梯'''
        if self.error == 1:  # 电梯出现故障
            return           # 不做处理
            
        '''改变电梯楼层'''
        if (self.floor not in self.target) and (self.floor not in self.mainWindow.up) and (self.floor not in self.mainWindow.down):
            if self.state == 1:              # 电梯处于向上状态
                self.floor = self.floor + 1  # 向上移动一层
            elif self.state == -1:           # 电梯处于向下状态
                self.floor = self.floor - 1  # 向下移动一层
        self.mainWindow.findChild(QLCDNumber, "{0}".format(self.id)).display(self.floor)  # 显示电梯楼层

        '''电梯处于向上状态'''
        if self.state == 1:
            self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉电梯内部按钮标识
            self.mainWindow.findChild(QPushButton, "up{0}".format(self.floor)).setStyleSheet("QPushButton{}")             # 去掉电梯外部按钮标识
            if (self.floor in self.target) or (self.floor in self.mainWindow.up):  # 到达目标楼层
                self.arrive = 1
            self.target.discard(self.floor)         # 从目标楼层集合中删除该层
            self.mainWindow.up.discard(self.floor)  # 从楼层上升集合中删除该层

            if len(list(self.target)) == 0:            # 目标楼层集合为空
                self.state = 0                         # 电梯进入静止状态
            elif max(list(self.target)) < self.floor:  # 最大目标楼层小于当前楼层
                self.state = -1                        # 电梯向下移动

        '''电梯处于向下状态'''
        if self.state == -1:
            self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉电梯内部按钮标识
            self.mainWindow.findChild(QPushButton, "down{0}".format(self.floor)).setStyleSheet("QPushButton{}")           # 去掉电梯外部按钮标识
            if (self.floor in self.target) or (self.floor in self.mainWindow.down):  # 到达目标楼层
                self.arrive = 1
            self.target.discard(self.floor)           # 从目标楼层集合中删除该层
            self.mainWindow.down.discard(self.floor)  # 从楼层下降集合中删除该层

            if len(list(self.target)) == 0:            # 目标楼层集合为空
                self.state = 0                         # 电梯进入静止状态
            elif min(list(self.target)) > self.floor:  # 最小目标楼层大于当前楼层
                self.state = 1                         # 电梯向上移动

        '''电梯处于静止状态'''            
        if self.state == 0:
            self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉电梯内部按钮标识
            self.mainWindow.findChild(QPushButton, "up{0}".format(self.floor)).setStyleSheet("QPushButton{}")             # 去掉电梯外部按钮标识
            self.mainWindow.findChild(QPushButton, "down{0}".format(self.floor)).setStyleSheet("QPushButton{}")           # 去掉电梯外部按钮标识
            
            if (self.floor in self.target) or (self.floor in self.mainWindow.up) or (self.floor in self.mainWindow.down):  # 到达目标楼层
                self.arrive = 1
            self.target.discard(self.floor)           # 从目标楼层集合中删除该层
            self.mainWindow.up.discard(self.floor)    # 从楼层上升集合中删除该层
            self.mainWindow.down.discard(self.floor)  # 从楼层下降集合中删除该层
            
            if len(list(self.target)) == 0:            # 目标楼层集合为空
                self.state = 0                         # 电梯进入静止状态
            elif max(list(self.target)) > self.floor:  # 最大目标楼层大于当前楼层
                self.state = 1                         # 电梯向上移动
            elif min(list(self.target)) < self.floor:  # 最小目标楼层小于当前楼层
                self.state = -1  # 电梯向上移动
        
    def change_error(self):
        '''改变电梯故障状态'''
        if self.error == 0:      # 电梯没有故障
            self.error = 1       # 设置为出现故障
            self.mainWindow.findChild(QPushButton, "error{0}".format(self.id)).setText("malfunction")  # 设置按钮文本
            self.target.clear()  # 清空目标楼层集合
            self.state = 0       # 设置电梯为静止状态
            for btnID in range(1, 21):
                self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, btnID)).setStyleSheet("QPushButton{}")  # 去掉电梯内部按钮标识
        else:                    # 电梯出现故障
            self.error = 0       # 设置为没有故障
            self.mainWindow.findChild(QPushButton, "error{0}".format(self.id)).setText("function")     # 设置按钮文本

    def add_target(self, floor):
        '''将楼层添加到电梯的目标楼层集合中'''
        # 找到对应的按钮
        self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, floor)).setStyleSheet("QPushButton{background-image: url(selected.png)}")
        # 将目标楼层添加到对应电梯的目标楼层集合中
        self.target.add(floor)