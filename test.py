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

    trigger = pyqtSignal(int)  # 实例化一个信号对象，传递int类型的参数

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

        # ----------------------------------------------------------------------------------------#
        self.move(10, 10)
        self.setWindowTitle('2051475 王浩')
        self.show()


    def set_up(self, floor):
        '''将楼层里的上楼请求添加到集合里'''
        # 找到对应的按钮，把背景设置为"background.png"
        myWindow.findChild(QPushButton, "up{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        self.up.add(floor)  # 将当前请求楼层添加到up集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)].index(
                min(abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)))].target.add(floor)


    def set_down(self, floor):
        '''将楼层里的下楼请求添加到集合里'''
        # 找到对应的按钮，把背景设置为"background.png"
        myWindow.findChild(QPushButton, "down{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        self.down.add(floor)    # 将当前请求楼层添加到down集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)].index(
                min(abs(self.Eles[0].floor - floor), abs(self.Eles[1].floor - floor), abs(self.Eles[2].floor - floor), abs(self.Eles[3].floor - floor), abs(self.Eles[4].floor - floor)))].target.add(floor)


if __name__ == '__main__':

    app = QApplication(sys.argv)  # 创建一个 QApplication 对象
    myWindow = MainWindow()       # 创建一个 MainWindow 对象

    sys.exit(app.exec_())         # 开始应用程序的主循环