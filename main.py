from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

from Window import *


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建一个 QApplication 对象
    myWindow = MainWindow()       # 创建一个 MainWindow 对象
    sys.exit(app.exec_())         # 开始应用程序的主循环