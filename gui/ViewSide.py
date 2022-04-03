# 查看下载侧边栏

import os
from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QGridLayout

from spider.Spider import Spider
from .component.Font import Font
from . import logger

class ViewSide(QFrame):

  def __init__(self, downloadDir, downloadList, addDownload, inform, *args):
    super().__init__(*args)
    self.downloadDir = downloadDir
    self.downloadList = downloadList
    self.addDownload = addDownload
    self.inform = inform
    self.initUI()
    # 将downloadDir中的东西加入到显示中
    self.addAll()

  def initUI(self):
    # 获取配置信息
    self.downloadCards = []
    # 基本布局结构
    self.layout_final = layout_final = QHBoxLayout()
    self.scroll = scroll = QScrollArea()
    self.scroll_widget = scroll_widget = QFrame()
    self.layout = layout = QVBoxLayout()
    self.setLayout(layout_final)
    layout_final.addWidget(scroll)
    scroll.setWidget(scroll_widget)
    scroll_widget.setLayout(layout)
    # 间距调整
    self.setFixedWidth(266)
    layout_final.setContentsMargins(0, 0, 0, 0)
    scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll_widget.setContentsMargins(0, 0, 0, 0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    # 样式调整
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
        width: 12px;
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
        height: 12px;
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

  def addDownloadCard(self, name, uid, route, exists = False):
    # 一个下载卡片
    downloadBox = QFrame()
    downloadLayout = QVBoxLayout()
    titleLine = QHBoxLayout()
    comboIcon = QIcon("icons/unselect.svg")
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
    accountID.setToolTip(name)
    accountID.setFont(Font.LEVEL3)
    # 根据小说还是图片更改颜色
    if Spider.isNovel(route):
          accountID.setStyleSheet(
        """
        color: #36ab60;
        """
      )
    else:
      accountID.setStyleSheet(
        """
        color: #1296db;
        """
      ) 
    upIcon = QIcon("icons/up.svg")
    upButton = QPushButton()
    upButton.setToolTip("上移")
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
    downButton.setToolTip("下移")
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
    openIcon = QIcon("icons/open_folder.svg")
    openButton = QPushButton()
    openButton.setToolTip("打开文件夹")
    openButton.setIcon(openIcon)
    openButton.setIconSize(QtCore.QSize(12, 12))
    openButton.setStyleSheet(
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
    addButton = QPushButton()
    if not exists:
      addIcon = QIcon("icons/add.svg")
      addButton.setToolTip("添加到下载项")
    else:
      addIcon = QIcon("icons/auth.svg")
      addButton.setToolTip("下载项中已存在")
    addButton.setIcon(addIcon)
    addButton.setIconSize(QtCore.QSize(12, 12))
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
    uidName = QLabel("用户UID：")
    typeName = QLabel("类   型：")
    uidLabel = QLabel(uid)
    typeLabel = QLabel(route)
    uidName.setFont(Font.LEVEL4)
    typeName.setFont(Font.LEVEL4)
    typeLabel.setFont(Font.LEVEL4)
    uidLabel.setFont(Font.LEVEL4)
    hbox = QHBoxLayout()
    gridBox = QGridLayout()
    gridBox.addWidget(uidName, 0, 0)
    gridBox.addWidget(uidLabel, 0, 1)
    gridBox.addWidget(typeName, 1, 0)
    gridBox.addWidget(typeLabel, 1, 1)
    hbox.addLayout(gridBox)
    hbox.addStretch(1)
    # 将各个组件加入其中
    titleLine.addWidget(comboButton)
    titleLine.addWidget(accountID)
    titleLine.addStretch(1)
    # titleLine.addWidget(upButton)
    # titleLine.addWidget(downButton)
    titleLine.addWidget(openButton)
    titleLine.addWidget(addButton)
    downloadLayout.addLayout(titleLine)
    downloadLayout.addSpacing(4)
    downloadLayout.addLayout(hbox)
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
      "exists": exists,
      "up": upButton,
      "down": downButton,
      "open": openButton,
      "add": addButton,
      "uid": uidLabel,
      "type": typeLabel,
      "name": accountID
    })
    pos = len(self.downloadCards) - 1
    comboButton.clicked.connect(lambda val, _pos = pos: self.switchSingle(_pos))
    downloadBox.mousePressEvent = lambda val, _pos = pos: self.switchSingle(_pos)
    openButton.clicked.connect(lambda : os.system(r'start "" "{}"'.format(os.path.join(self.downloadDir, uid, route))))
    addButton.clicked.connect(lambda val, _pos = pos: self.addDownloadItem(_pos))
    # 需实时刷新页面，然后调整大小，否则当事件触发结束时才会更新界面，导致下面的大小调整失效
    QApplication.processEvents()
    self.scroll_widget.adjustSize()
    # 将滚动条下滑到底部位置
    self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

  # 单选：更换下载选项卡的选择
  def switchSingle(self, pos):
    for i in range(len(self.downloadCards)):
      if i == pos:
        comboIcon = QIcon("icons/select.svg")
        self.downloadCards[i]["combo"].setIcon(comboIcon)
        self.downloadCards[i]["download"].setStyleSheet(
            """
            .QFrame {
            background-color: #e8f0ff;
            }
            """
        )
        self.downloadCards[i]["select"] = True
      else:
        comboIcon = QIcon("icons/unselect.svg")
        self.downloadCards[i]["combo"].setIcon(comboIcon)
        self.downloadCards[i]["download"].setStyleSheet(
            """
            .QFrame {
            background-color: transparent;
            }
            .QFrame:hover {
            background-color: rgb(238, 238, 238);
            }
            """
        )
        self.downloadCards[i]["select"] = False
    # 通知父亲 
    self.inform(os.path.join(self.downloadDir, self.downloadCards[pos]["uid"].text(), self.downloadCards[pos]["type"].text()))
        
  # 多选：更换下载选项卡的选择
  def switchMulti(self, pos):
    comboButton = self.downloadCards[pos]["combo"]
    downloadBox = self.downloadCards[pos]["download"]
    select = self.downloadCards[pos]["select"]
    if not select:
      comboIcon = QIcon("icons/unselect.svg")
      comboButton.setIcon(comboIcon)
      downloadBox.setStyleSheet(
        """
        .QFrame {
          background-color: #e8f0ff;
        }
        """
      )
    else:
      comboIcon = QIcon("icons/select.svg")
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
    # 通知父亲 
    self.inform(os.path.join(self.downloadDir, self.downloadCards[pos]["uid"].text(), self.downloadCards[pos]["type"].text()))

  def addAll(self):
    # 记录处于下载项中的
    hmap = {}
    for item in self.downloadList:
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
      hmap[str({"uid": uid, "route": route})] = name
    dirList = os.listdir(self.downloadDir)
    for dir in dirList:
      secondPath = os.path.join(self.downloadDir, dir)
      if os.path.isdir(secondPath):
        routes = Spider.getRoutes()
        for route in routes:
          if os.path.isdir(os.path.join(secondPath, route)):
            name = hmap.get(str({"uid": dir, "route": route}))
            if name != None:
              self.addDownloadCard(name, dir, route, True)
            else:
              self.addDownloadCard("{}({})".format(dir, route), dir, route, False)

  def delete(self, pos):
    item = self.downloadCards.pop(pos)
    item["download"].setParent(None)
    for i in range(len(self.downloadCards)):
      self.downloadCards[i]["combo"].clicked.disconnect()
      self.downloadCards[i]["add"].clicked.disconnect()
      self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switchSingle(_pos))
      self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switchSingle(_pos)
      self.downloadCards[i]["add"].clicked.connect(lambda val, _pos = i: self.addDownloadItem(_pos))
    self.scroll_widget.adjustSize()

  def deleteAll(self):
    containSelect = False
    for item in self.downloadCards:
      if item["select"]:
        containSelect = True
      item["download"].setParent(None)
    self.downloadCards = []
    self.scroll_widget.adjustSize()
    return containSelect

  def addDownloadItem(self, pos):
    item = self.downloadCards[pos]
    # 如果这里标识已存在（不管实际存不存在）都直接返回
    if item["exists"]:
      return
    if self.addDownload(item["name"].text(), item["uid"].text(), item["type"].text()) != False:
      addIcon = QIcon("icons/auth.svg")
      item["add"].setIcon(addIcon)
      item["add"].setToolTip("下载项中已存在")
      item["exists"] = True

  def update(self, newDownloadDir = None, newDownloadList = None):
    """
    刷新downloadDir和downloadList以及可能变动的文件信息
    """
    previousDownloadDir = self.downloadDir
    if newDownloadDir != None:
      self.downloadDir = newDownloadDir
    if newDownloadList != None:
      self.downloadList = newDownloadList
    # 记录处于下载项中的
    hmap = {}
    for item in self.downloadList:
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
      hmap[str({"uid": uid, "route": route})] = name
    # 记录downloadCards里面的信息
    hmap1 = {}
    # containSelect表示删除的项中是否包含当前选中的项
    containSelect = False
    # 如果下载路径不变（只要绝对路径相同即可），那么删除应该删除的项，保留应该保留的项并加入到hmap1中
    if os.path.abspath(previousDownloadDir) == os.path.abspath(self.downloadDir):
      # 应该删除的项
      removeList = []
      for i in range(len(self.downloadCards)):
        item = self.downloadCards[i]
        finalPath = os.path.join(self.downloadDir, item["uid"].text(), item["type"].text())
        if not os.path.isdir(finalPath):
          removeList.append(i)
        else:
          hmap1[str({"uid": item["uid"].text(), "route": item["type"].text()})] = i - len(removeList)
      # 将应该删除的项删除掉
      for i in range(len(removeList)):
        pos = removeList[i] - i
        item = self.downloadCards.pop(pos)
        if item["select"]:
          containSelect = True
        item["download"].setParent(None)
      # 剩余的项重新绑定事件
      for i in range(len(self.downloadCards)):
        self.downloadCards[i]["combo"].clicked.disconnect()
        self.downloadCards[i]["add"].clicked.disconnect()
        self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switchSingle(_pos))
        self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switchSingle(_pos)
        self.downloadCards[i]["add"].clicked.connect(lambda val, _pos = i: self.addDownloadItem(_pos))
      self.scroll_widget.adjustSize()
    else:
      containSelect = self.deleteAll()
    # 更新显示列表信息
    dirList = os.listdir(self.downloadDir)
    routes = Spider.getRoutes()
    for dir in dirList:
      secondPath = os.path.join(self.downloadDir, dir)
      if os.path.isdir(secondPath):
        for route in routes:
          if os.path.isdir(os.path.join(secondPath, route)):
            key = str({"uid": dir, "route": route})
            did = hmap1.get(key)
            if did == None:
              name1 = None
            else:
              name1 = self.downloadCards[did]["name"].text()
            name2 = hmap.get(key)
            if name1 == None:
              if name2 != None:
                self.addDownloadCard(name2, dir, route, True)
              else:
                self.addDownloadCard("{}({})".format(dir, route), dir, route, False)
            else:
              if name2 != None:
                addIcon = QIcon("icons/auth.svg")
                self.downloadCards[did]["add"].setIcon(addIcon)
                self.downloadCards[did]["add"].setToolTip("下载项中已存在")
                self.downloadCards[did]["exists"] = True
                if name2 != name1:
                  self.downloadCards[did]["name"].setText(name2)
              else:
                addIcon = QIcon("icons/add.svg")
                self.downloadCards[did]["add"].setIcon(addIcon)
                self.downloadCards[did]["add"].setToolTip("添加到下载项")
                self.downloadCards[did]["exists"] = False
    # 如果当前选中的项被删除，则需要通知父亲
    if containSelect:
      self.inform(False)
