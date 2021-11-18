# 侧边栏

from PyQt6 import QtCore
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QPushButton, QVBoxLayout
from .Font import Font
from .Account import Account

class Side(QFrame):

  def __init__(self, inform, *args):
    super().__init__(*args)
    # inform负责通知父亲选项切换
    self.inform = inform
    self.initUI()


  def initUI(self):
    userButton = QPushButton()
    downloadButton = QPushButton(" 下载")
    viewButton = QPushButton(" 查看")
    aboutButton = QPushButton(" 关于")
    settingButton = QPushButton(" 设置")

    # 将所有的按键对象全部存储在本对象中
    self.buttonList = [userButton, downloadButton, viewButton, settingButton, aboutButton]

    # 设置为checkable模式
    downloadButton.setCheckable(True)
    viewButton.setCheckable(True)
    settingButton.setCheckable(True)
    userButton.setCheckable(True)
    aboutButton.setCheckable(True)

    # 设置图标
    settingIcon = QIcon("icons/setting.svg")
    settingButton.setIcon(settingIcon)
    downloadIcon = QIcon("icons/download.svg")
    downloadButton.setIcon(downloadIcon)
    viewIcon = QIcon("icons/view.svg")
    viewButton.setIcon(viewIcon)
    aboutIcon = QIcon("icons/about.svg")
    aboutButton.setIcon(aboutIcon)

    # userButton单独设置固定高度
    userButton.setFixedHeight(80)

    # 设置布局
    vbox = QVBoxLayout()
    for button in self.buttonList:
      vbox.addWidget(button)
    vbox.addStretch(1)
    vbox.setSpacing(0)
    self.setLayout(vbox)

    # 布局更改
    vbox.setContentsMargins(0, 0, 0, 0)
    self.setContentsMargins(0, 0, 0, 0)

    # 设置每个按钮的点击事件
    for button in self.buttonList:
      button.clicked[bool].connect(self.pressButton)

    # 设置style
    buttonStyle = """
    QPushButton {
      padding-top: 10px;
      padding-bottom: 10px;
      background-color: rgb(245, 245, 245);
      border-bottom-width: 1px;
      border-bottom-style: solid;
      border-bottom-color: rgb(220, 220, 220);
      border: none;
    }
    QPushButton:hover {
      background-color: rgb(230, 230, 230);
    }
    QPushButton:checked {
      background-color: rgb(220, 220, 220);
    }
    """
    downloadButton.setStyleSheet(buttonStyle)
    viewButton.setStyleSheet(buttonStyle)
    settingButton.setStyleSheet(buttonStyle)
    userButton.setStyleSheet(buttonStyle)
    aboutButton.setStyleSheet(buttonStyle)
    downloadButton.setFont(Font.LEVEL3)
    viewButton.setFont(Font.LEVEL3)
    settingButton.setFont(Font.LEVEL3)
    userButton.setFont(Font.LEVEL3)
    aboutButton.setFont(Font.LEVEL3)
    downloadButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    viewButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    settingButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    userButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    aboutButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    self.setStyleSheet(
      """
      QFrame {
        background-color: rgb(245, 245, 245);
      }
      """
    )
    qds = QGraphicsDropShadowEffect()
    qds.setOffset(0, 0)
    qds.setColor(QColor(200, 200, 200))
    qds.setBlurRadius(15)
    self.setGraphicsEffect(qds)
    # self.raise_()
    
  def pressButton(self, val):
    pressObj = self.sender()
    if not val:
      pressObj.setChecked(True)
    else:
      if self.inform(self.buttonList.index(pressObj)):
        for button in self.buttonList:
          if button != pressObj:
            button.setChecked(False)
        pressObj.setChecked(True)
      else:
        pressObj.setChecked(False)

  # 点击val编号的按钮从而切换视图
  def changeView(self, val):
    if val >= len(self.buttonList) or val < 0:
      return
    self.buttonList[val].click()

  # 更改状态
  def stateChange(self, state):
    if state == Account.State.NONE or state == Account.State.UNKNOWN:
      userIcon = QIcon("icons/user.svg")
    elif state == Account.State.ERROR or state == Account.State.NETWORK_ANOMALY:
      userIcon = QIcon("icons/cry.svg")
    elif state == Account.State.OK:
      userIcon = QIcon("icons/smile.svg")
    elif state == Account.State.QUERY:
      userIcon = QIcon("icons/query.svg")
    else:
      userIcon = QIcon("icons/user.svg")
    self.buttonList[0].setIcon(userIcon)
    self.buttonList[0].setIconSize(QSize(60, 60))
      
