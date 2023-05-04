from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from functools import partial

from Elevator import *


class MainWindow(QWidget):
    '''创建一个名为MainWindow的类模拟程序界面，继承QWidget类'''

    def __init__(self):
        '''构造函数'''
        super().__init__()   # 调用父类QWidget的构造函数

        self.up = set([])    # 楼层的向上请求
        self.down = set([])  # 楼层的向下请求
        
        self.Eles = []       # 创建5个电梯线程
        for i in range(1, 6):
            self.Eles.append(Elevator(i, self))

        self.setUI()         # 设置界面布局

        for i in range(5):   # 启动5个电梯进程
            self.Eles[i].start()
        
    def setUI(self):
        '''界面设置函数'''
        wholeLayout = QHBoxLayout()  # 创建横向的总体布局
        gridLeft = QGridLayout()     # 创建左侧网格布局：电梯视图
        gridRight = QGridLayout()    # 创建右侧网格布局：楼层视图
        gridLeft.setSpacing(0)       # 设置间隔为0
        gridRight.setSpacing(0)      # 设置间隔为0

        widgeLeft = QWidget()              # 创建QWidget部件
        widgeLeft.setLayout(gridLeft)      # 采用左侧网格布局
        wholeLayout.addWidget(widgeLeft)   # 部件加至全局布局

        widgeRight = QWidget()             # 创建QWidget部件
        widgeRight.setLayout(gridRight)    # 采用右侧网格布局
        wholeLayout.addWidget(widgeRight)  # 部件加至全局布局

        palette = QPalette()                                       # 创建颜色集
        palette.setColor(QPalette.Background, QColor(68, 70, 84))  # 设置背景色
        self.setPalette(palette)                                   # 应用背景色

        self.setLayout(wholeLayout)  # 窗口设置全局布局

        btnNames = [('%s' % i) for i in range(1, 21)]                 # 电梯按钮编号
        btnPositions = [(i, j) for j in range(2) for i in range(10)]  # 电梯按钮位置
        btnUp = [('▲ %s' % i) for i in range(1, 21)]                  # 楼层上升按钮
        btnDown = [('▼ %s' % i) for i in range(1, 21)]                # 楼层下降按钮
        
        '''电梯视图'''
        
        # 数码显示管
        for eleID in range(5):
            self.lcd = QLCDNumber()                                # 创建数码显示管
            self.lcd.setObjectName("{0}".format(eleID + 1))        # 设置数码显示管对象名称
            paletteLCD = self.lcd.palette()                                    # 创建颜色集
            paletteLCD.setColor(paletteLCD.WindowText, QColor(236, 236, 241))  # 设置字体色
            self.lcd.setPalette(paletteLCD)                                    # 应用字体色
            gridRight.addWidget(self.lcd, 0, 3 * eleID, 2, 2)      # 添加到右侧的网格布局
            self.lab = QLabel(self)                                # 创建增加缝隙的实例
            gridRight.addWidget(self.lab, 0, 3 * eleID + 2, 1, 1)  # 添加到右侧的网格布局
            
        # 故障报警按钮
        for eleID in range(5):
            self.button = QPushButton("function")                                # 创建带有文本的按钮
            self.button.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))        # 设置按钮文本字体
            self.button.setObjectName("error{0}".format(eleID + 1))              # 设置按钮对象名称
            self.button.setMinimumHeight(50)                                     # 设置按钮最小高度
            paletteBTN = self.button.palette()
            paletteBTN.setColor(paletteBTN.ButtonText, QColor(77, 120, 204))
            self.button.setPalette(paletteBTN)
            self.button.clicked.connect(partial(self.Eles[eleID].change_error))  # 连接到函数
            gridRight.addWidget(self.button, 12, 3 * eleID, 1, 2)                # 添加到右侧的网格布局
        
        # 电梯门开关状态
        for eleID in range(5):
            self.button = QPushButton()                             # 创建没有文本的按钮
            self.button.setObjectName("open{0}".format(eleID + 1))  # 设置按钮对象名称
            self.button.setMinimumHeight(80)                        # 设置按钮最小高度
            gridRight.addWidget(self.button, 13, 3 * eleID, 1, 2)   # 添加到右侧的网格布局

        # 楼层按钮
        for eleID in range(5):  # 电梯编号：1~5
            btnID = 1           # 楼层按钮编号：1~20
            for position, name in zip(btnPositions, btnNames):  # 枚举电梯按钮的编号和位置
                if name == '':
                    continue
                self.button = QPushButton(name)                                           # 创建带有文本的按钮
                self.button.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))             # 设置按钮文本字体
                self.button.setObjectName("{0}+{1}".format(eleID + 1, btnID))             # 设置按钮对象名称
                self.button.clicked.connect(partial(self.Eles[eleID].add_target, btnID))  # 连接到函数
                btnID = btnID + 1
                self.button.setMaximumHeight(60)  # 设置按钮最大高度
                gridRight.addWidget(self.button, position[0] + 2, position[1] + eleID * 3)  # 添加到右侧的网格布局

        for i in range(gridRight.rowCount()):     # 枚举右侧布局中的每一行
            gridRight.setRowMinimumHeight(i, 60)  # 设置每行最小高度

        '''楼层视图'''
        upFloor = 1
        for i in btnUp:
            self.button = QPushButton(i)                                # 创建带有文本的按钮
            self.button.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))   # 设置按钮文本字体
            self.button.setObjectName("up{0}".format(upFloor))          # 设置按钮对象名称
            self.button.setMinimumHeight(42)                            # 设置按钮最小高度
            self.button.clicked.connect(partial(self.set_up, upFloor))  # 连接到函数 
            gridLeft.addWidget(self.button, 20 - upFloor + 1, 0)        # 添加到左侧的网格布局第20-upFloor+1行和第0列
            upFloor = upFloor + 1

        downFloor = 1
        for i in btnDown:
            self.button = QPushButton(i)                                    # 创建带有文本的按钮
            self.button.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))       # 设置按钮文本字体
            self.button.setObjectName("down{0}".format(downFloor))          # 设置按钮对象名称
            self.button.setMinimumHeight(42)                                # 设置按钮最小高度
            self.button.clicked.connect(partial(self.set_down, downFloor))  # 连接到函数 
            gridLeft.addWidget(self.button, 20 - downFloor + 1, 1)          # 添加到左侧的网格布局第20-downFloor+1行和第0列
            downFloor = downFloor + 1

        '''整体窗口'''
        self.move(50, 50)                       # 设置窗口在屏幕上的初始位置
        self.setWindowTitle('2051475 wanghao')  # 设置窗口标题
        self.show()                             # 显示窗口控件

    def set_up(self, floor):
        '''将楼层里的上楼请求添加到集合里'''
        # 找到对应的按钮
        self.findChild(QPushButton, "up{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(selected.png)}")
        self.up.add(floor)  # 把楼层添加到up集合中
        # 寻找可用的运行中电梯
        available_elevators = []
        for ele in self.Eles:
            if ele.error == 1:  # 该电梯故障
                continue
            elif ele.floor == floor and ele.state == 0:   # 电梯处于目标楼层且静止
                ele.target.add(floor)
                return
            elif ele.state == 1 and ele.floor <= floor:   # 目标在电梯上升路径上
                available_elevators.append(ele)
            elif ele.state == 0:                          # 电梯处于静止状态
                available_elevators.append(ele)
        # 选择距离最近的电梯
        if available_elevators:
            available_elevators.sort(key=lambda x: abs(x.floor - floor))
            available_elevators[0].target.add(floor)
            return 
        # 没有符合条件的电梯则选择一个空闲电梯
        for ele in self.Eles:
            if ele.error == 0:  # 该电梯故障
                ele.target.add(floor)
                return
            
    def set_down(self, floor):
        '''将楼层里的下楼请求添加到集合里'''
        # 找到对应的按钮
        self.findChild(QPushButton, "down{0}".format(floor)).setStyleSheet("QPushButton{background-image: url(selected.png)}")
        self.down.add(floor)    # 把楼层添加到down集合中
        # 寻找可用的运行中电梯
        available_elevators = []
        for ele in self.Eles:
            if ele.error == 1:  # 该电梯故障
                continue
            elif ele.floor == floor and ele.state == 0:   # 电梯处于目标楼层且静止
                ele.target.add(floor)
                return
            elif ele.state == -1 and ele.floor >= floor:  # 目标在电梯下降路径上
                available_elevators.append(ele)
            elif ele.state == 0:                          # 电梯处于静止状态
                available_elevators.append(ele)
        # 选择距离最近的电梯
        if available_elevators:
            available_elevators.sort(key=lambda x: abs(x.floor - floor))
            available_elevators[0].target.add(floor)
            return 
        # 没有符合条件的电梯则选择一个空闲电梯
        for ele in self.Eles:
            if ele.error == 0:  # 该电梯故障
                ele.target.add(floor)
                return