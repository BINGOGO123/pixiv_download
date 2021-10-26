# 主界面

from PyQt6.QtGui import QIcon, QValidator
from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
from component.About import About

from component.Account import Account
from component.Download import Download
from component.Setting import Setting
from component.Side import Side
from component.View import View

class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()

    self.initUI()

  def initUI(self):
    # 基本信息
    self.resize(800, 500)
    self.setMinimumSize(500, 500)
    self.setWindowTitle(' Pixiv下载工具')
    self.setWindowIcon(QIcon("icons/pixiv.svg"))
    self.center()
    # self.statusBar()
    self.show()
    # self.setStyleSheet(
    #   """
    #   QMainWindow {
    #     background-color: white;
    #   }
    #   """
    # )

    # 布局信息
    widget = QWidget()
    hbox = QHBoxLayout()

    # 右边区域
    account = Account()
    download = Download()
    view = View()
    about = About()
    setting = Setting()
    self.viewList = [account, download, view, about, setting]
    for right in self.viewList:
      right.setHidden(True)

    # 左侧边栏，必须先设置右边再设置左边，因为一开始side会自动点击一个按钮
    side = Side(self.changeView)
    # 设置固定宽度110
    side.setFixedWidth(110)

    # 设置布局
    hbox.addWidget(side)
    for right in self.viewList:
      hbox.addWidget(right)
    widget.setLayout(hbox)
    self.setCentralWidget(widget)

  def center(self):
    qr = self.frameGeometry()
    cp = self.screen().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

  def changeView(self, option):
    for pos in range(len(self.viewList)):
      if pos != option and not self.viewList[pos].isHidden():
        if self.viewList[pos].switchOut():
          self.viewList[pos].setHidden(True)
        else:
          # 如果部件拒绝切换，那么操作就此作废
          return False
    self.viewList[option].setHidden(False)
    return True
    
  # 窗口关闭事件
  def closeEvent(self, event):
    for right in self.viewList:
      if not right.isHidden():
        if not right.switchOut():
          event.ignore()
          break
    else:
        event.accept()