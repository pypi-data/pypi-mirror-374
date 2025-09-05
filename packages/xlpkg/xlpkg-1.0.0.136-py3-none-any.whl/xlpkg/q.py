"""
PyQt相关
"""
import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QColor, QKeySequence as QKSQ,QDesktopServices as QDS
from PyQt5.QtWidgets import QAction as QA, QShortcut as QSC,QWidget
from PyQt5.QtWidgets import QTableWidget as QTW, QTableWidgetItem as QTWI, QDialog as QDL, QVBoxLayout as QVBLY, \
    QApplication as QAPP, QMenu, QMessageBox as QMB, \
    QGroupBox as QGB, QRadioButton as QRB, QPushButton as QPB, QHBoxLayout as QHBLY, QMainWindow as QMW,QFileDialog as QFD,QD

# 设置窗体居中显示
def f_setcenter(self, w, h):
    # 获取主屏幕的信息
    from PyQt5.QtGui import QScreen
    screen = QAPP.primaryScreen()

    # 获取屏幕的分辨率（宽度和高度）
    screen_size = screen.size()

    # 计算窗口的初始位置（屏幕中心）
    width, height = 400, 300
    x = (screen_size.width() - width) // 2
    y = (screen_size.height() - height) // 2

    # 使用self.setGeometry()设置窗口的初始位置和大小
    self.setGeometry(x, y, width, height)
    x = (screen)
    pass

def f_exit(self, event):
    r0 = QMB.question(self, "提示", "确定退出?", QMB.StandardButton.Yes | QMB.StandardButton.No)
    if r0 == QMB.StandardButton.Yes:
        r1 = QMB.question(self, "提示", "再次确定退出?",
                                  QMB.StandardButton.Yes | QMB.StandardButton.No)
        if r1 == QMB.StandardButton.Yes:
            sys.exit()
        else:
            print('No')
    pass

class Filedialog(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        b_01 = QPB("OK", self)

        self.resize(800, 600)
        self.show()
        b_01.clicked.connect(self.f_ok)

    def f_ok(self):
        fname, _ = QFD.getOpenFileName(self, "Open file", '/', "Images(*.jpg *.gif)")
        print(fname)

    pass

# 关于
def f_msgabout(msg):
    QMB.about('about', msg)
    pass

# 错误
def f_msgcritical(msg):
    QMB.critical('Error', msg)
    pass

# 警告
def f_msgwarn(msg):
    QMB.warning('Warn', msg)
    pass

# 消息
def f_msginfo(msg):
    QMB.information('Info', msg)
    pass

# 询问
def f_msgquestion(msg):
    QMB.question('Question', msg)
    pass

def f_openurl(self, url):
    QDS.openUrl(QUrl(url))
    pass

def f_add(a,b):
    return(a+b)
    pass
