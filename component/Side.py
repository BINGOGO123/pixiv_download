# 侧边栏

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout

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
    self.buttonList = [userButton, downloadButton, viewButton, aboutButton, settingButton]

    # 设置为checkable模式
    downloadButton.setCheckable(True)
    viewButton.setCheckable(True)
    settingButton.setCheckable(True)
    userButton.setCheckable(True)
    aboutButton.setCheckable(True)

    # 设置图标
    userIcon = QIcon("icons/user.svg")
    userButton.setIcon(userIcon)
    userButton.setIconSize(QSize(60, 60))
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
    vbox.addWidget(userButton)
    vbox.addWidget(downloadButton)
    vbox.addWidget(viewButton)
    vbox.addWidget(aboutButton)
    vbox.addWidget(settingButton)
    vbox.addStretch(1)
    self.setLayout(vbox)

    # 布局更改
    vbox.setContentsMargins(0, 0, 0, 0)
    # self.setAutoFillBackground(True)
    # self.setFrameShape(QFrame.Shape.StyledPanel)
    # self.setFrameShadow(QFrame.Shadow.Sunken)

    # 设置每个按钮的点击事件
    for button in self.buttonList:
      button.clicked[bool].connect(self.pressButton)
    # 开始时点击一下userButton
    userButton.click()
    
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
          
