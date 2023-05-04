from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import time
from functools import partial

from Elevator import *

class MainWindow(QWidget):
    '''
    主窗口
    '''

    def __init__(self):
        '''构造函数'''
        super().__init__()   # 调用父类QWidget的构造函数

        self.up = set([])    # 楼层的向上请求
        self.down = set([])  # 楼层的向下请求
        
        self.Eles = []       # 创建5个电梯线程
        for i in range(1, 6):
            self.Eles.append(Elevator(i, self))

        self.initUI()        # 设置界面布局

        for i in range(5):   # 启动5个电梯进程
            self.Eles[i].start()
        
    def initUI(self):
        wlayout = QHBoxLayout()  # 总体布局：横向，其中嵌套了两个网格布局
        gridoutright = QGridLayout()
        grid = QGridLayout()
        grid.setSpacing(0)
        gridoutright.setSpacing(0)
        gwg = QWidget()  # 准备部件
        rightwg = QWidget()
        gwg.setLayout(grid)  # 部件设置局部布局
        rightwg.setLayout(gridoutright)
        wlayout.addWidget(gwg)  # 部件加至全局布局
        wlayout.addWidget(rightwg)
        self.setLayout(wlayout)  # 窗体本体设置全局布局
        names = [('%s' % i) for i in range(1, 21)]  # 电梯按钮编号
        positions = [(i, j) for j in range(2) for i in range(10)]  # 位置

        nameforallup = [('▲ %s' % i) for i in range(1, 21)]  # 走廊里的按钮，向上
        nameforalldown = [('▼ %s' % i) for i in range(1, 21)]  # 向下
        # --------------------------------------下面是左边布局--------------------------------------#
        for inti in range(5):
            intj = 1
            for position, name in zip(positions, names):
                if name == '':
                    continue
                self.button = QPushButton(name)
                self.button.setFont(QFont("Microsoft YaHei", 12))
                self.button.setObjectName("{0}+{1}".format(inti + 1, intj))
                self.button.clicked.connect(partial(self.Eles[inti].add_target, intj))
                intj = intj + 1
                self.button.setMaximumHeight(60)  # 按钮最大高度
                grid.addWidget(self.button, position[0] + 2, position[1] + inti * 3)

        for i in range(5):
            self.lcd = QLCDNumber()  # 数字显示
            # self.lcd.setStyleSheet("QLCDNumber{background-image: url(open.png)}")
            self.lcd.setObjectName("{0}".format(i + 1))
            grid.addWidget(self.lcd, 0, 3 * i, 2, 2)
            self.lab = QLabel(self)  # 这几个label是为了增加缝隙
            grid.addWidget(self.lab, 0, 3 * i + 2, 1, 1)
        for i in range(grid.rowCount()):
            grid.setRowMinimumHeight(i, 60)

        # 暂停按钮
        for i in range(5):
            self.button = QPushButton("暂停")
            self.button.setFont(QFont("Microsoft YaHei", 12))
            self.button.setObjectName("pause{0}".format(i + 1))
            self.button.setMinimumHeight(40)
            '''error'''
            self.button.clicked.connect(lambda: self.Eles[int(i)].pause())
            #self.button.clicked.connect(lambda: self.Eles[i].pause())  
            #self.button.clicked.connect(partial(self.Eles[i].pause))
            grid.addWidget(self.button, 12, 3 * i, 1, 2)

        # OPEN显示在下面的按钮上
        for i in range(5):
            self.button = QPushButton()
            self.button.setObjectName("open{0}".format(i + 1))
            self.button.setMinimumHeight(80)
            grid.addWidget(self.button, 13, 3 * i, 1, 2)

        # --------------------------------------下面是右边布局--------------------------------------#
        fori = 0
        for i in nameforallup:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft YaHei"))
            self.button.setObjectName("up{0}".format(fori + 1))
            self.button.setMinimumHeight(42)
            self.button.clicked.connect(partial(self.set_up, fori + 1))
            gridoutright.addWidget(self.button, 20 - fori, 0)
            fori = fori + 1

        fori = 0
        for i in nameforalldown:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft YaHei"))
            self.button.setObjectName("down{0}".format(fori + 1))
            self.button.setMinimumHeight(42)
            self.button.clicked.connect(partial(self.set_down, fori + 1))
            gridoutright.addWidget(self.button, 20 - fori, 1)
            fori = fori + 1

        self.move(50, 50)                       # 设置窗口在屏幕上的初始位置
        self.setWindowTitle('2051475 wanghao')  # 设置窗口标题
        self.show()                             # 显示窗口控件

    '''调度算法待定'''
    def set_up(self, floor):
        '''将楼层里的上楼请求添加到集合里'''
        # 找到对应的按钮，把背景设置为"background.png"
        self.findChild(QPushButton, "up{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        self.up.add(floor)  # 把楼层添加到up集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)].index(
                min(abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)))].target.add(floor)
    '''调度算法待定'''
    def set_down(self, floor):
        '''将楼层里的下楼请求添加到集合里'''
        # 找到对应的按钮，把背景设置为"background.png"
        self.findChild(QPushButton, "down{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        self.down.add(floor)    # 把楼层添加到down集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)].index(
                min(abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)))].target.add(floor)
