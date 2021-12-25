# 下载管理界面

import sys
import PyQt6
from PyQt6 import QtCore
from PyQt6.QtCore import QFileSelector, QRegularExpression
from PyQt6.QtGui import QColor, QCursor, QFont, QIcon, QImage, QIntValidator, QPixmap, QRegularExpressionValidator, QTextCursor, QTextLine, QValidator
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget, QPushButton, QScrollArea, QScrollBar, QScroller, QVBoxLayout, QWidget, QPlainTextEdit

from spider.Spider import Spider
from .component.Font import Font
from .component.LineEdit import LineEdit
from .component.ComboBox import ComboBox
from config import base_config
from . import logger


class CreateDownload(QWidget):
  def __init__(self, upper, name = "", uid = "", type = "bookmarks/artworks", *args):
    super().__init__(*args)
    self.upper = upper
    self.initUI(name, uid, type)
    self.changeState()
    self.show()
  def initUI(self, name, uid, type):
    self.setWindowIcon(QIcon("icons/pixiv.svg"))
    self.setWindowTitle(" 新建下载对象")
    self.setFixedSize(300, 160)
    self.setWindowFlag(QtCore.Qt.WindowType.Dialog)
    self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    self.setStyleSheet(
      """
      QWidget {
        background-color: white;
      }
      """
    )
    hbox = QHBoxLayout()
    hbox.addStretch(1)
    vbox = QVBoxLayout()
    vbox.addStretch(1)
    self.nameEdit = LineEdit("名   称", name, self.changeState, Font.LEVEL4)
    self.uidEdit = LineEdit("用户UID", uid, self.changeState, Font.LEVEL4, True)
    self.typeEdit = ComboBox("类   型", type, ["bookmarks/artworks", "bookmarks/novels", "illustrations", "novels"], self.changeState, Font.LEVEL4)
    vbox.addWidget(self.nameEdit)
    vbox.addWidget(self.uidEdit)
    vbox.addWidget(self.typeEdit)
    hbox.addLayout(vbox)
    hbox.addStretch(1)
    self.saveButton = QPushButton(" 确定")
    self.quitButton = QPushButton(" 取消")
    self.saveButton.setFont(Font.LEVEL4)
    self.quitButton.setFont(Font.LEVEL4)
    saveIcon = QIcon("icons/save.svg")
    self.saveButton.setIcon(saveIcon)
    quitIcon = QIcon("icons/close.svg")
    self.quitButton.setIcon(quitIcon)
    self.saveButton.setFixedWidth(100)
    self.quitButton.setFixedWidth(100)
    self.saveButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        border-radius: 8px;
        background-color: rgb(220, 230, 240);
        padding: 7px 10px 7px 10px;
      }
      QPushButton:hover {
        background-color: rgb(200, 220, 240);
      }
      QPushButton:pressed {
        background-color: rgb(180, 210, 240);
      }
      """
    )
    self.quitButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        border-radius: 8px;
        background-color: rgb(240, 220, 220);
        padding: 7px 10px 7px 10px;
      }
      QPushButton:hover {
        background-color: rgb(240, 200, 200);
      }
      QPushButton:pressed {
        background-color: rgb(240, 180, 180);
      }
      """
    )
    buttonBox = QHBoxLayout()
    buttonBox.addWidget(self.saveButton)
    buttonBox.addWidget(self.quitButton)
    vbox.addSpacing(15)
    vbox.addLayout(buttonBox)
    vbox.addStretch(1)
    self.setLayout(hbox)
    self.quitButton.clicked.connect(self.close)
    self.saveButton.clicked.connect(lambda : (self.close(), self.upper.addDownload(*self.getInfo())))
  def getInfo(self):
    return [self.nameEdit.getValue(), self.uidEdit.getValue(), self.typeEdit.getValue()]
  def changeState(self):
    info = self.getInfo()
    for one in info:
      if one == "":
        self.saveButton.setDisabled(True)
        return
    self.saveButton.setDisabled(False)

class Download(QFrame):

  def __init__(self, *args):
    super().__init__(*args)

    self.initUI()

  def initUI(self):
    # 获取配置信息
    downloadList = base_config["__main__"]["main"]["download_list"]
    self.downloadCards = []
    # 选项列表布局
    self.layout = layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    # 循环创建卡片并加入layout
    for item in downloadList:
      if type(item) == dict:
        name = item["name"]
        url = item["url"]
        try:
          uid, route = Spider.url_analyze(url)
        except TypeError:
          logger.exception("{} 解析失败".format(url))
          continue
      elif type(item) == str:
        url = item
        try:
          uid, route = Spider.url_analyze(url)
        except TypeError:
          logger.exception("{} 解析失败".format(url))
          continue
        name = "{}({})".format(uid, route)
      else:
        logger.error("{} 类型错误".format(item))
        continue
      # 一个下载卡片
      downloadBox = QFrame()
      downloadLayout = QVBoxLayout()
      titleLine = QHBoxLayout()
      comboIcon = QIcon("icons/combox.svg")
      comboButton = QPushButton()
      comboButton.setIcon(comboIcon)
      comboButton.setIconSize(QtCore.QSize(12, 12))
      comboButton.setStyleSheet(
        """
        QPushButton {
          border: none;
          padding: 2px; 
          border-radius:3px;
        }
        """
      )
      accountID = QLabel(name)
      accountID.setFont(Font.LEVEL3)
      upIcon = QIcon("icons/up.svg")
      upButton = QPushButton()
      upButton.setIcon(upIcon)
      upButton.setIconSize(QtCore.QSize(12, 12))
      upButton.setStyleSheet(
        """
        QPushButton {
          border: none;
          padding: 2px; 
          border-radius:3px;
        }
        QPushButton:hover {
          background-color: rgb(200, 200, 200);
        }
        QPushButton:pressed {
          background-color:rgb(150, 150, 150);
        }
        """
      )
      downIcon = QIcon("icons/down.svg")
      downButton = QPushButton()
      downButton.setIcon(downIcon)
      downButton.setIconSize(QtCore.QSize(12, 12))
      downButton.setStyleSheet(
        """
        QPushButton {
          border: none;
          padding: 2px; 
          border-radius:3px;
        }
        QPushButton:hover {
          background-color: rgb(200, 200, 200);
        }
        QPushButton:pressed {
          background-color:rgb(150, 150, 150);
        }
        """
      )
      editIcon = QIcon("icons/edit.svg")
      editButton = QPushButton()
      editButton.setIcon(editIcon)
      editButton.setIconSize(QtCore.QSize(12, 12))
      editButton.setStyleSheet(
        """
        QPushButton {
          border: none;
          padding: 2px; 
          border-radius:3px;
        }
        QPushButton:hover {
          background-color: rgb(200, 200, 200);
        }
        QPushButton:pressed {
          background-color:rgb(150, 150, 150);
        }
        """
      )
      deleteIcon = QIcon("icons/delete.svg")
      deleteButton = QPushButton()
      deleteButton.setIcon(deleteIcon)
      deleteButton.setIconSize(QtCore.QSize(12, 12))
      deleteButton.setStyleSheet(
        """
        QPushButton {
          border: none;
          padding: 2px; 
          border-radius:3px;
        }
        QPushButton:hover {
          background-color: rgb(200, 200, 200);
        }
        QPushButton:pressed {
          background-color:rgb(150, 150, 150);
        }
        """
      )
      uidLabel = QLabel("用户ID：{}".format(uid))
      typeLabel = QLabel("类  型：{}".format(route))
      typeLabel.setFont(Font.LEVEL4)
      uidLabel.setFont(Font.LEVEL4)
      # 将各个组件加入其中
      titleLine.addWidget(comboButton)
      titleLine.addWidget(accountID)
      titleLine.addStretch(1)
      titleLine.addWidget(upButton)
      titleLine.addWidget(downButton)
      titleLine.addWidget(editButton)
      titleLine.addWidget(deleteButton)
      downloadLayout.addLayout(titleLine)
      downloadLayout.addSpacing(4)
      downloadLayout.addWidget(uidLabel)
      downloadLayout.addWidget(typeLabel)
      downloadLayout.setContentsMargins(6, 6, 6, 6)
      downloadLayout.setSpacing(4)
      downloadBox.setLayout(downloadLayout)
      downloadBox.setFixedWidth(254)
      downloadBox.setStyleSheet(
        """
        .QFrame {
          background-color: rgb(240, 240, 240);
          background-color: rgb(250, 250, 250);
          background-color: rgb(238, 238, 238);
          background-color: rgb(238, 238, 238);
          background-color: white;
          background-color: transparent;

        }
        .QFrame:hover {
          background-color: rgb(240, 240, 240);
          background-color: rgb(250, 250, 250);
          background-color: rgb(238, 238, 238);
          background-color: white;
          background-color: transparent;
          background-color: rgb(238, 238, 238);
        }
        """
      )
      layout.addWidget(downloadBox)
      self.downloadCards.append({
        "combo": comboButton,
        "download": downloadBox,
        "select": False,
        "up": upButton,
        "down": downButton,
        "edit": editButton,
        "delete": deleteButton,
        "uid": uidLabel,
        "type": typeLabel,
        "name": accountID
      })
    layout.addStretch(1)

    # 选中事件绑定
    for pos in range(len(self.downloadCards)):
      comboButton = self.downloadCards[pos]["combo"]
      downloadBox = self.downloadCards[pos]["download"]
      upButton = self.downloadCards[pos]["up"]
      downButton = self.downloadCards[pos]["down"]
      editButton = self.downloadCards[pos]["edit"]
      deleteButton = self.downloadCards[pos]["delete"]
      comboButton.clicked.connect(lambda val, _pos = pos: self.switch(_pos))
      downloadBox.mousePressEvent = lambda val, _pos = pos: self.switch(_pos)
      upButton.clicked.connect(lambda val, _pos = pos: self.up(_pos))
      downButton.clicked.connect(lambda val, _pos = pos: self.down(_pos))
      editButton.clicked.connect(lambda val, _pos = pos: self.edit(_pos))
      deleteButton.clicked.connect(lambda val, _pos = pos: self.delete(_pos))


    layout_function = QHBoxLayout()
    startIcon = QIcon("icons/start.svg")
    startButton = QPushButton()
    startButton.setIconSize(QtCore.QSize(24, 24))
    startButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    startButton.setIcon(startIcon)
    terminateIcon = QIcon("icons/terminate.svg")
    terminateButton = QPushButton()
    terminateButton.setIconSize(QtCore.QSize(24, 24))
    terminateButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    terminateButton.setIcon(terminateIcon)
    addIcon = QIcon("icons/add.svg")
    addButton = QPushButton()
    addButton.setIconSize(QtCore.QSize(24, 24))
    addButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    addButton.setIcon(addIcon)
    deleteIcon = QIcon("icons/delete.svg")
    deleteButton = QPushButton()
    deleteButton.setIconSize(QtCore.QSize(24, 24))
    deleteButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    deleteButton.setIcon(deleteIcon)
    layout_function.addWidget(startButton)
    layout_function.addSpacing(5)
    # layout_function.addWidget(terminateButton)
    # layout_function.addSpacing(5)
    layout_function.addWidget(addButton)
    layout_function.addSpacing(5)
    layout_function.addWidget(deleteButton)
    layout_function.addStretch(1)
    function_widget = QFrame()
    function_widget.setLayout(layout_function)

    layout_display = QVBoxLayout()
    layout_display.addWidget(QLabel("text"))
    layout_display.addWidget(QLabel("text"))
    layout_display.addWidget(QLabel("text"))
    layout_display.addWidget(QLabel("text"))
    layout_display.addWidget(QLabel("text"))

    # 功能区事件绑定
    addButton.clicked.connect(self.add)

    layout_final = QVBoxLayout()
    layout_final.addWidget(function_widget)
    layout_h = QHBoxLayout()
    scroll = QScrollArea()
    scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    self.scroll_widget = scroll_widget = QFrame()
    scroll_widget.setLayout(layout)
    scroll_widget.setContentsMargins(0, 0, 0, 0)
    scroll.setFixedWidth(260)
    # 设置滚动区域的最小尺寸，因为在父亲上面设置了最小尺寸，所以这里就不用设置了
    # scroll.setMinimumSize(300, 400)
    # scrollarea 作为一个组件，可以设置窗口
    scroll.setWidget(scroll_widget)
    # 设置没有边框
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    layout_h.addWidget(scroll)
    layout_h.addLayout(layout_display)
    layout_h.setContentsMargins(0, 0, 0, 0)
    layout_h.setSpacing(0)
    layout_final.addLayout(layout_h)
    layout_final.setContentsMargins(0, 0, 0, 0)
    layout_final.setSpacing(0)
    self.setLayout(layout_final)

    # 最终样式修改
    scroll_widget.setStyleSheet(
      """
      QFrame {
        background-color: transparent;
      }
      """
    )
    scroll.setStyleSheet(
      """
      QScrollArea {
        background-color: transparent;
      }
      QScrollBar:vertical
      {
        width:6px;
        background-color: rgb(200, 200, 200);
      }
      QScrollBar::handle:vertical
      {
        background-color: rgb(200, 200, 200);
        margin-left:0px;
        margin-right:0px;
      }
      QScrollBar::handle:vertical:hover
      {
        background:rgb(180, 180, 180);
      }
      QScrollBar:horizontal
      {
        height:6px;
        background-color: rgb(200, 200, 200);
      }
      QScrollBar::handle:horizontal
      {
        background-color: rgb(200, 200, 200);
        margin-left:0px;
        margin-right:0px;
      }
      QScrollBar::handle:horizontal:hover
      {
        background:rgb(180, 180, 180);
      }
      """
    )
    qds = QGraphicsDropShadowEffect()
    qds.setOffset(0, 0)
    qds.setColor(QColor(200, 200, 200))
    qds.setBlurRadius(15)
    function_widget.setGraphicsEffect(qds)
    function_widget.setStyleSheet(
      """
      QFrame {
        background-color: rgb(240, 240, 240);
        background-color: white;
        background-color: transparent;
        background-color: rgb(250, 250, 250);
        background-color: rgb(238, 238, 238);
      }
      """
    )

  # 更换下载选项卡的选择
  def switch(self, pos):
    comboButton = self.downloadCards[pos]["combo"]
    downloadBox = self.downloadCards[pos]["download"]
    select = self.downloadCards[pos]["select"]
    if not select:
      comboIcon = QIcon("icons/combox_select.svg")
      comboButton.setIcon(comboIcon)
      downloadBox.setStyleSheet(
        """
        .QFrame {
          background-color: #e8f0ff;
        }
        """
      )
    else:
      comboIcon = QIcon("icons/combox.svg")
      comboButton.setIcon(comboIcon)
      downloadBox.setStyleSheet(
        """
        .QFrame {
          background-color: transparent;
        }
        .QFrame:hover {
          background-color: rgb(238, 238, 238);
        }
        """
      )
    self.downloadCards[pos]["select"] = not select

  def up(self, pos):
    pass
  
  def down(self, pos):
    pass

  def edit(self, pos):
    pass

  def delete(self, pos):
    pass

  def add(self):
    self.child = CreateDownload(self)

  def addDownload(self, name, uid, type):
    # 一个下载卡片
    downloadBox = QFrame()
    downloadLayout = QVBoxLayout()
    titleLine = QHBoxLayout()
    comboIcon = QIcon("icons/combox.svg")
    comboButton = QPushButton()
    comboButton.setIcon(comboIcon)
    comboButton.setIconSize(QtCore.QSize(12, 12))
    comboButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      """
    )
    accountID = QLabel(name)
    accountID.setFont(Font.LEVEL3)
    upIcon = QIcon("icons/up.svg")
    upButton = QPushButton()
    upButton.setIcon(upIcon)
    upButton.setIconSize(QtCore.QSize(12, 12))
    upButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    downIcon = QIcon("icons/down.svg")
    downButton = QPushButton()
    downButton.setIcon(downIcon)
    downButton.setIconSize(QtCore.QSize(12, 12))
    downButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    editIcon = QIcon("icons/edit.svg")
    editButton = QPushButton()
    editButton.setIcon(editIcon)
    editButton.setIconSize(QtCore.QSize(12, 12))
    editButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    deleteIcon = QIcon("icons/delete.svg")
    deleteButton = QPushButton()
    deleteButton.setIcon(deleteIcon)
    deleteButton.setIconSize(QtCore.QSize(12, 12))
    deleteButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
        border-radius:3px;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    uidLabel = QLabel("用户ID：{}".format(uid))
    typeLabel = QLabel("类  型：{}".format(type))
    typeLabel.setFont(Font.LEVEL4)
    uidLabel.setFont(Font.LEVEL4)
    # 将各个组件加入其中
    titleLine.addWidget(comboButton)
    titleLine.addWidget(accountID)
    titleLine.addStretch(1)
    titleLine.addWidget(upButton)
    titleLine.addWidget(downButton)
    titleLine.addWidget(editButton)
    titleLine.addWidget(deleteButton)
    downloadLayout.addLayout(titleLine)
    downloadLayout.addSpacing(4)
    downloadLayout.addWidget(uidLabel)
    downloadLayout.addWidget(typeLabel)
    downloadLayout.setContentsMargins(6, 6, 6, 6)
    downloadLayout.setSpacing(4)
    downloadBox.setLayout(downloadLayout)
    downloadBox.setFixedWidth(254)
    downloadBox.setStyleSheet(
      """
      .QFrame {
        background-color: rgb(240, 240, 240);
        background-color: rgb(250, 250, 250);
        background-color: rgb(238, 238, 238);
        background-color: rgb(238, 238, 238);
        background-color: white;
        background-color: transparent;

      }
      .QFrame:hover {
        background-color: rgb(240, 240, 240);
        background-color: rgb(250, 250, 250);
        background-color: rgb(238, 238, 238);
        background-color: white;
        background-color: transparent;
        background-color: rgb(238, 238, 238);
      }
      """
    )
    self.layout.addWidget(downloadBox)
    self.downloadCards.append({
      "combo": comboButton,
      "download": downloadBox,
      "select": False,
      "up": upButton,
      "down": downButton,
      "edit": editButton,
      "delete": deleteButton,
      "uid": uidLabel,
      "type": typeLabel,
      "name": accountID
    })

    pos = len(self.downloadCards) - 1
    comboButton = self.downloadCards[pos]["combo"]
    downloadBox = self.downloadCards[pos]["download"]
    upButton = self.downloadCards[pos]["up"]
    downButton = self.downloadCards[pos]["down"]
    editButton = self.downloadCards[pos]["edit"]
    deleteButton = self.downloadCards[pos]["delete"]
    comboButton.clicked.connect(lambda val, _pos = pos: self.switch(_pos))
    downloadBox.mousePressEvent = lambda val, _pos = pos: self.switch(_pos)
    upButton.clicked.connect(lambda val, _pos = pos: self.up(_pos))
    downButton.clicked.connect(lambda val, _pos = pos: self.down(_pos))
    editButton.clicked.connect(lambda val, _pos = pos: self.edit(_pos))
    deleteButton.clicked.connect(lambda val, _pos = pos: self.delete(_pos))
    

  def save(self):
    downloadList = []
    for pos in range(len(self.downloadCards)):
      uidLabel = self.downloadCards[pos]["uid"]
      typeLabel = self.downloadCards[pos]["type"]
      nameLabel = self.downloadCards[pos]["name"]
      url = Spider.url_package(uidLabel.text(), typeLabel.text())
      downloadList.append({
        "name": nameLabel.text(),
        "url": url
      })
    base_config["__main__"]["main"]["download_list"] = downloadList

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return True
    
  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    return self.canSwitchOut()