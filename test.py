import sys
import time
from functools import partial

from PyQt5.QtCore import QThread, pyqtSignal  # 导入PyQt信号类和QThread类
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Elevator(QThread):
    '''
    创建一个名为Elevator的类，继承QThread类
    '''
    trigger = pyqtSignal(int)  # 实例化一个信号对象，传递int类型的参数

    def __init__(self, id, mainWindow):
        '''类的构造函数，接收int类型的参数'''
        super(Elevator, self).__init__()  # 调用父类QThread的构造函数
        self.mainWindow = mainWindow

        self.id = id                     # 保存参数id
        self.trigger.connect(self.check)       # 将信号trigger连接到check函数
        self.should_sleep = 0
        self.should_sleep2 = 0
        self.pause = 1  # 电梯是否暂停运行
        self.state = 0  # 电梯状态 0表示停止 1表示向上运行 -1表示向下运行
        self.floor = 1  # 电梯当前所在楼层
        self.target = set([])  # 目标楼层

    def run(self):
        '''重写QThread的run方法'''
        while (1):
            # 如果should_sleep列表的self.int-1项为1，则执行以下代码
            if self.should_sleep == 1:
                # 设置id为"open{0}".format(self.int)的QPushButton按钮的样式为指定的背景图片
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.int)).setStyleSheet(
                    "QPushButton{background-image: url(open.png)}")
                time.sleep(2)  # 线程休眠2秒
                # 将id为"open{0}".format(self.int)的QPushButton按钮的样式设置为空
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.int)).setStyleSheet(
                    "QPushButton{}")
                self.should_sleep = 0  # 将should_sleep列表的self.int-1项设置为0

            # 如果should_sleep列表的self.int-1+5项为1，则执行以下代码
            if self.should_sleep2 == 1:
                # 设置id为"open{0}".format(self.int)的QPushButton按钮的样式为指定的背景图片
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.int)).setStyleSheet(
                    "QPushButton{background-image: url(open.png)}")
                time.sleep(2)  # 线程休眠2秒
                # 将id为"open{0}".format(self.int)的QPushButton按钮的样式设置为空
                self.mainWindow.findChild(QPushButton, "open{0}".format(self.int)).setStyleSheet(
                    "QPushButton{}")
                self.should_sleep2 = 0  # 将should_sleep列表的self.int-1+5项设置为0
            
            self.trigger.emit(self.id)  # 发射信号trigger，并传递参数self.id
            time.sleep(1)  # 线程休眠1秒
    
    def check(self):
        if self.pause == 1:  # 如果电梯当前处于暂停状态
            # 改变电梯楼层
            if self.state == 0:  # 如果电梯当前处于静止状态
                pass
            elif self.state == 1:  # 如果电梯当前处于向上状态
                self.floor = self.floor + 1  # 电梯当前楼层向上移动一层
            else:  # 如果电梯当前处于向下状态
                self.floor = self.floor - 1  # 电梯当前楼层向下移动一层
        
            self.mainWindow.findChild(QLCDNumber, "{0}".format(id)).display(self.floor)  # 显示电梯楼层
            self.mainWindow.findChild(QPushButton, "{0}+{1}".format(id, self.floor)).setStyleSheet("QPushButton{}")  # 去掉该层的标识

            # 从外部等候楼层中移除该层
            if self.state == 1:  # 如果电梯当前处于向上状态
                self.mainWindow.findChild(QPushButton, "up{0}".format(self.floor)).setStyleSheet("QPushButton{}")  # 移除标识
            if self.state == -1:  # 如果电梯当前处于向下状态
                self.mainWindow.findChild(QPushButton, "down{0}".format(self.floor)).setStyleSheet("QPushButton{}")  # 移除标识

            if self.state == 1:  # 如果电梯当前处于向上状态
                if (self.floor in self.target) or (self.floor in people_up):
                    self.should_sleep = 1  # 该电梯需要继续执行
            if self.state == -1:  # 如果电梯当前处于向下状态
                if (self.floor in self.target) or (self.floor in people_down):
                    self.should_sleep2 = 1  # 该电梯需要继续执行

            if self.state == 1:  # 如果电梯当前处于向上状态
                people_up.discard(self.floor)  # 从楼层等待列表中移除该层
            if self.state == -1:  # 如果电梯当前处于向下状态
                people_down.discard(self.floor)  # 从楼层等待列表中移除该层
            self.target.discard(self.floor)  # 从要达到的目标楼层中移除该层

            # ----------------------状态改变的算法---------------------- #
            if self.state == 1:  # 如果当前状态是向上
                # 如果当前电梯要到达的目标楼层列表为空，说明电梯已经没有任务，状态置为0，表示电梯静止等待。
                if len(list(self.target)) == 0:
                    self.state = 0
                # 如果电梯要到达的目标楼层列表不为空，且列表中最大的目标楼层小于当前楼层，说明电梯应该向下运动，状态置为-1，表示电梯正在向上运动。
                if (len(list(self.target)) != 0) and (max(list(self.target)) < self.floor):
                    self.state = -1
            
            if self.state == -1:  # 如果当前状态是向下
                # 如果当前电梯要到达的目标楼层列表为空，说明电梯已经没有任务，状态置为0，表示电梯静止等待。
                if len(list(self.target)) == 0:
                    self.state = 0
                # 如果电梯要到达的目标楼层列表不为空，且列表中最小的目标楼层大于当前楼层，说明电梯应该向上运动，状态置为1，表示电梯正在向上运动。
                if (len(list(self.target)) != 0) and (min(list(self.target)) > self.floor):
                    self.state = 1
            
            if self.state == 0:  # 如果当前状态是静止
                # 如果电梯内有要到达的楼层并且电梯内的目标楼层最大值大于当前电梯所在的楼层
                if (len(list(self.target)) != 0) and (max(list(self.target)) > self.floor):
                    self.state = 1  # 向上运动
                # 如果电梯内有要到达的楼层并且电梯内的目标楼层最小值小于当前电梯所在的楼层
                if (len(list(self.target)) != 0) and (min(list(self.target)) < self.floor):
                    self.state = -1  # 向下运动
            
            # -----------------------显示电梯楼层----------------------- #
            self.mainWindow.findChild(QLCDNumber, "{0}".format(id)).display(self.floor)
            # ------------------------间隔的时间------------------------ #
        
    def pause(self):
        if self.pause == 0:  # 如果该电梯未被暂停
            self.pause = 1  # 将该电梯的暂停状态设为已暂停
            self.mainWindow.findChild(QPushButton, "pause{0}".format(self.id)).setText("暂停")  # 将该电梯对应的暂停按钮文本设置为“暂停”
        else:  # 如果该电梯已被暂停
            self.pause = 0  # 将该电梯的暂停状态设为未暂停
            self.mainWindow.findChild(QPushButton, "pause{0}".format(self.id)).setText("启动")  # 将该电梯对应的暂停按钮文本设置为“启动”

    def set_goal(self, flr):  # 设定目标楼层
        '''将目标楼层添加到对应电梯的目标楼层集合中'''
        # 找到对应的按钮，并设置样式为背景图片为background.png
        self.mainWindow.findChild(QPushButton, "{0}+{1}".format(self.id, flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        self.target.add(flr)  # 将目标楼层添加到对应电梯的目标楼层集合中


class MainWindow(QWidget):  # 主窗口

    def __init__(self):
        super(MainWindow, self).__init__()

        # 五个线程对应五部电梯，每隔一定时间检查每部电梯的状态和elevator_goal数组，并作出相应的行动
        self.Eles = []
        for i in range(1, 6):
            self.Eles.append(Elevator(i, self))
        
        for i in range(5):
            self.Eles[i].start()
        
        self.initUI()

    def initUI(self):
        # 设置背景图片
        # palette = QPalette()
        # palette.setBrush(QPalette.Background, QBrush(QPixmap("beijing.png")))
        # self.setPalette(palette)

        wlayout = QHBoxLayout()  # 总体布局：横向，其中嵌套了两个网格布局，emmmm 目前总体感觉还行，不想花时间美化了，先写业务逻辑
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
                self.button.clicked.connect(partial(self.Eles[inti].set_goal, intj))
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
            self.button.clicked.connect(lambda: self.Eles[i].pause())
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
            self.button.clicked.connect(partial(self.set_global_goal_up, fori + 1))
            gridoutright.addWidget(self.button, 20 - fori, 0)
            fori = fori + 1

        fori = 0
        for i in nameforalldown:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft YaHei"))
            self.button.setObjectName("down{0}".format(fori + 1))
            self.button.setMinimumHeight(42)
            self.button.clicked.connect(partial(self.set_global_goal_down, fori + 1))
            gridoutright.addWidget(self.button, 20 - fori, 1)
            fori = fori + 1

        # ----------------------------------------------------------------------------------------#
        self.move(10, 10)
        self.setWindowTitle('Elevator-Dispatching Copyright@2020 沈天宇')
        self.show()


    def set_global_goal_up(self, flr):  # 设定楼道里上楼请求所在的楼层
        '''将楼道里的上楼请求添加到对应的电梯的目标楼层中'''
        # 找到对应的按钮，并将其背景设置为"background.png"
        myWindow.findChild(QPushButton, "up{0}".format(flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        people_up.add(flr)  # 将当前请求楼层添加到people_up集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - flr), abs(self.Eles[1].floor - flr), abs(self.Eles[2].floor - flr), abs(self.Eles[3].floor - flr), abs(self.Eles[4].floor - flr)].index(
                min(abs(self.Eles[0].floor - flr), abs(self.Eles[1].floor - flr), abs(self.Eles[2].floor - flr), abs(self.Eles[3].floor - flr), abs(self.Eles[4].floor - flr)))].add(flr)


    def set_global_goal_down(self, flr):  # 设定楼道里下楼请求所在的楼层
        '''将楼道里的下楼请求添加到对应的电梯的目标楼层中'''
        # 找到对应的按钮，并将其背景设置为"background.png"
        myWindow.findChild(QPushButton, "down{0}".format(flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
        people_down.add(flr)    # 将当前请求楼层添加到people_down集合中
        # 计算电梯到每个楼层的距离，将请求楼层添加到距离最近的电梯的目标楼层中
        self.Eles[
            [abs(self.Eles[0].floor - flr), abs(self.Eles[1].floor - flr), abs(self.Eles[2].floor - flr), abs(self.Eles[3].floor - flr), abs(self.Eles[4].floor - flr)].index(
                min(abs(self.Eles[0].floor - flr), abs(self.Eles[1].floor - flr), abs(self.Eles[2].floor - flr), abs(self.Eles[3].floor - flr), abs(self.Eles[4].floor - flr)))].add(flr)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    myWindow = MainWindow()

    # 表示楼道里的向上的请求
    people_up = set([])

    # 表示楼道里的向下的请求
    people_down = set([])

    sys.exit(app.exec_())  # 应用程序主循环