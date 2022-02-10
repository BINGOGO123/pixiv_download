# 下载管理界面
from enum import Enum
import os
import threading
from PyQt6 import QtCore
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QApplication, QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
import ctypes

from spider.Spider import Spider
from .component.Font import Font
from .component.LineEdit import LineEdit
from .component.ComboBox import ComboBox
from .component.DownloadItem import DownloadItem
from .component.DownloadNovel import DownloadNovel
from .component.StartDownload import StartDownload
from .component.EndDownload import EndDownload
from config import base_config
from . import logger
from tool.tool import saveJson


class CreateDownload(QWidget):
  def __init__(self, upper, name = "", uid = "", type = "bookmarks/artworks", pos = None, title = "新建下载对象", *args):
    super().__init__(*args)
    self.upper = upper
    self.initUI(name, uid, type, pos, title)
    self.changeState()
    self.show()
  def initUI(self, name, uid, type, pos, title):
    self.setWindowIcon(QIcon("icons/pixiv.svg"))
    self.setWindowTitle(" " + title)
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
    self.typeEdit = ComboBox("类   型", type, Spider.getRoutes(), self.changeState, Font.LEVEL4)
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
    if pos != None:
      self.saveButton.clicked.connect(lambda : (self.close(), self.upper.editItem(pos, *self.getInfo())))
    else:
      self.saveButton.clicked.connect(lambda : (self.close(), self.upper.addItem(*self.getInfo())))
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
  class State(Enum):
    SELECTED = "已选择"
    NOT_SELECT = "未选择"
    DOWNLOADING = "下载中"
    STOPPING = "终止中"


  def customEvent(self, e):
    if e.type() == StateChangeEvent.idType:
      # 如果state不为None，则更改为state状态，否则根据选择状况更新state
      if e.state != None:
        self.state = e.state
      else:
        self.stateChange()
    elif e.type() == AddContentEvent.idType:
      content = e.content
      update = content.get("update")
      itemType = content.get("type")
      if update == True:
        if itemType == "image":
          if len(self.downloadItemList) == 0:
            logger.error("Download 更新image时gallery数量为0")
            return
          try:
            url = str(content.get("url"))
            path = None if content.get("path") == None else str(content.get("path"))
            method = str(content.get("method"))
            color = None if content.get("color") == None else str(content.get("color"))
          except Exception as e:
            logger.error("Download 更新image时content格式错误，content={}".format(content))
            return
          if type(self.downloadItemList[-1]) != DownloadItem:
            logger.error("Download 更新image时上一个对象不是DownloadItem，content={}".format(content))
            return
          imageCount = self.downloadItemList[-1].imageCount()
          if imageCount == 0:
            logger.error("Download 更新image时gallery中的image数量为0，content={}".format(content))
            return
          self.downloadItemList[-1].changeImage(imageCount - 1, url, path, method, color)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "novel":
          if len(self.downloadItemList) == 0:
            logger.error("Download 更新novel时series数量为0")
            return
          try:
            url = str(content.get("url"))
            path = None if content.get("path") == None else str(content.get("path"))
            method = str(content.get("method"))
            color = None if content.get("color") == None else str(content.get("color"))
          except Exception as e:
            logger.error("Download 更新novel时content格式错误，content={}".format(content))
            return
          if type(self.downloadItemList[-1]) != DownloadNovel:
            logger.error("Download 更新novel时上一个对象不是DownloadNovel，content={}".format(content))
            return
          novelCount = self.downloadItemList[-1].novelCount()
          if novelCount == 0:
            logger.error("Download 更新novel时gallery中的novel数量为0，content={}".format(content))
            return
          self.downloadItemList[-1].changeNovel(novelCount - 1, url, path, method, color)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        else:
          logger.error("Download 无法执行AddContentEvent操作，content={}".format(content))
      else:
        if itemType == "gallery":
          try:
            title = str(content.get("title"))
            url = str(content.get("url"))
          except Exception as e:
            logger.error("Download 新增gallery时content格式错误，content={}".format(content))
            return
          imageList = []
          downloadItem = DownloadItem(self.count, title, url, imageList)
          self.scroll_info_layout.addWidget(downloadItem)
          self.count += 1
          self.downloadItemList.append(downloadItem)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "image":
          if len(self.downloadItemList) == 0:
            logger.error("Download 新增image时gallery数量为0")
            return
          try:
            url = str(content.get("url"))
            path = None if content.get("path") == None else str(content.get("path"))
            method = str(content.get("method"))
            color = None if content.get("color") == None else str(content.get("color"))
          except Exception as e:
            logger.error("Download 新增image时content格式错误，content={}".format(content))
            return
          self.downloadItemList[-1].addImage(url, path, method, color)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "series":
          try:
            title = str(content.get("title"))
            url = str(content.get("url"))
          except Exception as e:
            logger.error("Download 新增series时content格式错误，content={}".format(content))
            return
          novelList = []
          downloadNovel = DownloadNovel(self.count, title, url, novelList)
          self.scroll_info_layout.addWidget(downloadNovel)
          self.count += 1
          self.downloadItemList.append(downloadNovel)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "novel":
          if len(self.downloadItemList) == 0:
            logger.error("Download 新增novel时series数量为0")
            return
          try:
            url = str(content.get("url"))
            path = None if content.get("path") == None else str(content.get("path"))
            method = str(content.get("method"))
            color = None if content.get("color") == None else str(content.get("color"))
          except Exception as e:
            logger.error("Download 新增novel时content格式错误，content={}".format(content))
            return
          self.downloadItemList[-1].addNovel(url, path, method, color)
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "start":
          # 重置日志记录编号
          self.count = 1
          # 重置下载记录（之前的记录不再记录）
          self.downloadItemList = []
          name = str(content.get("name"))
          uid = str(content.get("uid"))
          route = str(content.get("route"))
          self.scroll_info_layout.addWidget(StartDownload(name, uid, route))
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        elif itemType == "end":
          name = str(content.get("name"))
          uid = str(content.get("uid"))
          route = str(content.get("route"))
          self.scroll_info_layout.addWidget(EndDownload(name, uid, route))
          # 刷新页面并滑到底部
          QApplication.processEvents()
          self.scroll_info_frame.adjustSize()
          self.scroll_info.verticalScrollBar().setValue(self.scroll_info.verticalScrollBar().maximum())
        else:
          logger.error("Download 无法执行AddContentEvent操作，content={}".format(content))


  @property
  def state(self):
    return self._state
  @state.setter
  def state(self, new_val):
    self._state = new_val
    if self._state == self.State.NOT_SELECT:
      startIcon = QIcon("icons/start.svg")
      self.startButton.setIcon(startIcon)
      self.startButton.disconnect()
      self.startButton.clicked.connect(self.startAllDownload)
      self.startButton.setDisabled(True)
      self.startButton.setToolTip("选择下载项后下载")
      self.deleteButton.setDisabled(True)
      self.deleteButton.setToolTip("选择下载项后删除")
      self.addButton.setDisabled(False)
      self.scroll_widget.setDisabled(False)
      self.clearButton.setDisabled(False)
    elif self._state == self.State.SELECTED:
      startIcon = QIcon("icons/start.svg")
      self.startButton.setIcon(startIcon)
      self.startButton.disconnect()
      self.startButton.clicked.connect(self.startAllDownload)
      self.startButton.setDisabled(False)
      self.startButton.setToolTip("开始所选下载项")
      self.deleteButton.setDisabled(False)
      self.deleteButton.setToolTip("删除所选下载项")
      self.addButton.setDisabled(False)
      self.scroll_widget.setDisabled(False)
      self.clearButton.setDisabled(False)
    elif self._state == self.State.DOWNLOADING:
      startIcon = QIcon("icons/terminate.svg")
      self.startButton.setIcon(startIcon)
      self.startButton.disconnect()
      self.startButton.clicked.connect(self.stopDownload)
      self.startButton.setToolTip("正在下载")
      self.deleteButton.setDisabled(True)
      self.addButton.setDisabled(True)
      self.scroll_widget.setDisabled(True)
      self.clearButton.setDisabled(True)
    elif self._state == self.State.STOPPING:
      startIcon = QIcon("icons/terminate.svg")
      self.startButton.setIcon(startIcon)
      self.startButton.disconnect()
      self.startButton.clicked.connect(self.stopDownload)
      self.startButton.setToolTip("正在终止")
      self.startButton.setDisabled(True)
      self.deleteButton.setDisabled(True)
      self.addButton.setDisabled(True)
      self.scroll_widget.setDisabled(True)
      self.clearButton.setDisabled(True)
    # 未知状态
    else:
      logger.error("Download 未知状态：{}".format(self._state))
      startIcon = QIcon("icons/start.svg")
      self.startButton.setIcon(startIcon)
      self.startButton.disconnect()
      self.startButton.clicked.connect(self.startAllDownload)
      self.startButton.setToolTip("选择下载项后下载")
      self.startButton.setDisabled(True)
      self.deleteButton.setToolTip("选择下载项后删除")
      self.deleteButton.setDisabled(True)
      self.addButton.setDisabled(True)
      self.scroll_widget.setDisabled(True)
      self.clearButton.setDisabled(False)
    # 通知父亲状态改变
    self.inform(self._state)

  def __init__(self, inform, *args):
    super().__init__(*args)
    self.inform = inform
    # 下载线程
    self.download = None
    # 日志记录编号
    self.count = 1
    # 日志对象记录
    self.downloadItemList = []
    self.initUI()
    # 根据按钮状态更新state
    self.stateChange()

  def initUI(self):
    # 获取配置信息
    downloadList = base_config["__main__"]["main"]["download_list"]
    self.downloadCards = []
    # 选项列表布局
    self.scroll = scroll = QScrollArea()
    self.scroll_widget = scroll_widget = QFrame()
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
      self.addDownloadCard(name, uid, route)
    # 加了这个会导致后续难以增加新的下载项（位置错乱），而且不加这个也不会影响布局，所以注释掉了
    # layout.addStretch(1)

    layout_function = QHBoxLayout()
    startIcon = QIcon("icons/start.svg")
    self.startButton =  startButton = QPushButton()
    startButton.setToolTip("开始所有下载项")
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
    addIcon = QIcon("icons/add.svg")
    self.addButton = addButton = QPushButton()
    addButton.setToolTip("新建下载对象")
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
    self.deleteButton = deleteButton = QPushButton()
    deleteButton.setToolTip("删除所选下载项")
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
    clearIcon = QIcon("icons/clear.svg")
    self.clearButton = clearButton = QPushButton()
    clearButton.setToolTip("删除所有下载记录")
    clearButton.setIconSize(QtCore.QSize(24, 24))
    clearButton.setStyleSheet(
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
    clearButton.setIcon(clearIcon)
    layout_function.addWidget(startButton)
    layout_function.addSpacing(5)
    # layout_function.addSpacing(5)
    layout_function.addWidget(addButton)
    layout_function.addSpacing(5)
    layout_function.addWidget(deleteButton)
    layout_function.addStretch(1)
    layout_function.addSpacing(5)
    layout_function.addWidget(clearButton)
    function_widget = QFrame()
    function_widget.setLayout(layout_function)

    # 右边下载信息展示区域
    self.scroll_info = scroll_info = QScrollArea()
    self.scroll_info_frame = scroll_info_frame = QFrame()
    self.scroll_info_layout = scroll_info_layout = QVBoxLayout()
    # scroll_info_layout.addWidget(DownloadItem(
    #   99999,
    #   "一个下载项",
    #   "https://wwww.bingoz.cn", [
    #     {
    #       "url": "https://wwww.bingoz.cn",
    #       "path": r"""D:\project\pixiv_download\downloaded\55109945\bookmarks\artworks\裸足＋白丝⑤+布鲁马_84958496_1.jpg""",
    #       "method": "下载"
    #     },
    #     {
    #       "url": "https://wwww.bingoz.cn",
    #       "path": r"""D:\project\pixiv_download\downloaded\55109945\bookmarks\artworks\裸足＋白丝⑤+布鲁马_84958496_1.jpg""",
    #       "method": "下载"
    #     },
    #     {
    #       "url": "https://wwww.bingoz.cn",
    #       "path": r"""D:\project\pixiv_download\downloaded\55109945\bookmarks\artworks\裸足＋白丝⑤+布鲁马_84958496_1.jpg""",
    #       "method": "下载"
    #     }
    #   ]
    # ))
    scroll_info_layout_outline = QVBoxLayout()
    scroll_info_layout_outline.addLayout(scroll_info_layout)
    scroll_info_layout_outline.addStretch(1)
    scroll_info_layout.setSpacing(10)
    scroll_info_frame.setLayout(scroll_info_layout_outline)
    scroll_info_frame.setContentsMargins(0, 0, 0, 0)
    # scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    scroll_info.setWidget(scroll_info_frame)
    scroll_info.setFrameShape(QFrame.Shape.NoFrame)
    scroll_info.setWidgetResizable(True)
    scroll_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

    # 功能区事件绑定
    addButton.clicked.connect(self.add)
    deleteButton.clicked.connect(self.deleteSelect)
    startButton.clicked.connect(self.startAllDownload)
    clearButton.clicked.connect(self.clearDownload)

    layout_final = QVBoxLayout()
    layout_final.addWidget(function_widget)
    layout_h = QHBoxLayout()
    scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    scroll_widget.setLayout(layout)
    scroll_widget.setContentsMargins(0, 0, 0, 0)
    scroll.setFixedWidth(266)
    # 设置滚动区域的最小尺寸，因为在父亲上面设置了最小尺寸，所以这里就不用设置了
    # scroll.setMinimumSize(300, 400)
    # scrollarea 作为一个组件，可以设置窗口
    scroll.setWidget(scroll_widget)
    # 设置没有边框
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    layout_h.addWidget(scroll)
    layout_h.addWidget(scroll_info)
    layout_h.setContentsMargins(0, 0, 0, 0)
    layout_h.setSpacing(0)
    layout_final.addLayout(layout_h)
    layout_final.setContentsMargins(0, 0, 0, 0)
    layout_final.setSpacing(0)
    self.setLayout(layout_final)

    # 最终样式修改
    scroll_info_frame.setStyleSheet(
      """
      QFrame {
        background-color: transparent;
      }
      """
    )
    scroll_info.setStyleSheet(
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

  def addDownloadCard(self, name, uid, route):
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
    editIcon = QIcon("icons/edit.svg")
    editButton = QPushButton()
    editButton.setToolTip("编辑")
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
    deleteButton.setToolTip("删除")
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
    titleLine.addWidget(upButton)
    titleLine.addWidget(downButton)
    titleLine.addWidget(editButton)
    titleLine.addWidget(deleteButton)
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
      "up": upButton,
      "down": downButton,
      "edit": editButton,
      "delete": deleteButton,
      "uid": uidLabel,
      "type": typeLabel,
      "name": accountID
    })
    pos = len(self.downloadCards) - 1
    comboButton.clicked.connect(lambda val, _pos = pos: self.switch(_pos))
    downloadBox.mousePressEvent = lambda val, _pos = pos: self.switch(_pos)
    upButton.clicked.connect(lambda val, _pos = pos: self.up(_pos))
    downButton.clicked.connect(lambda val, _pos = pos: self.down(_pos))
    editButton.clicked.connect(lambda val, _pos = pos: self.edit(_pos))
    deleteButton.clicked.connect(lambda val, _pos = pos: self.delete(_pos))
    # 需实时刷新页面，然后调整大小，否则当事件触发结束时才会更新界面，导致下面的大小调整失效
    QApplication.processEvents()
    self.scroll_widget.adjustSize()
    # 将滚动条下滑到底部位置
    self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
    
  def editItem(self, pos, name, uid, type):
    item = self.downloadCards[pos]
    nameBackup = item["name"].text()
    uidBackup = item["uid"].text()
    typeBackup = item["type"].text()
    item["name"].setText(name)
    item["uid"].setText(uid)
    item["type"].setText(type)
    # 如果保存失败则回退修改
    if self.save() == False:
      item["name"].setText(nameBackup)
      item["uid"].setText(uidBackup)
      item["type"].setText(typeBackup)

  def addItem(self, name, uid, type):
    self.addDownloadCard(name, uid, type)
    # 尝试保存，若失败则回退操作
    if self.save() == False:
      item = self.downloadCards.pop(len(self.downloadCards) - 1)
      item["download"].setParent(None)
      self.scroll_widget.adjustSize()
      return

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
    self.stateChange()

  def up(self, pos):
    if pos <= 0:
      return
    item = self.downloadCards.pop(pos)
    self.downloadCards.insert(pos - 1, item)
    # 如果保存失败，则回退操作并返回
    if self.save() == False:
      self.downloadCards.insert(pos, self.downloadCards.pop(pos - 1))
      return
    item["download"].setParent(None)
    self.layout.insertWidget(pos - 1, item["download"])
    # 重新绑定功能按键
    for i in range(len(self.downloadCards)):
      self.downloadCards[i]["combo"].clicked.disconnect()
      self.downloadCards[i]["up"].clicked.disconnect()
      self.downloadCards[i]["down"].clicked.disconnect()
      self.downloadCards[i]["edit"].clicked.disconnect()
      self.downloadCards[i]["delete"].clicked.disconnect()
      self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switch(_pos))
      self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switch(_pos)
      self.downloadCards[i]["up"].clicked.connect(lambda val, _pos = i: self.up(_pos))
      self.downloadCards[i]["down"].clicked.connect(lambda val, _pos = i: self.down(_pos))
      self.downloadCards[i]["edit"].clicked.connect(lambda val, _pos = i: self.edit(_pos))
      self.downloadCards[i]["delete"].clicked.connect(lambda val, _pos = i: self.delete(_pos))
  
  def down(self, pos):
    if pos >= len(self.downloadCards) - 1:
      return
    item = self.downloadCards.pop(pos)
    self.downloadCards.insert(pos + 1, item)
    # 如果保存失败，则回退操作并返回
    if self.save() == False:
      self.downloadCards.insert(pos, self.downloadCards.pop(pos + 1))
      return
    item["download"].setParent(None)
    self.layout.insertWidget(pos + 1, item["download"])
    # 重新绑定功能按键
    for i in range(len(self.downloadCards)):
      self.downloadCards[i]["combo"].clicked.disconnect()
      self.downloadCards[i]["up"].clicked.disconnect()
      self.downloadCards[i]["down"].clicked.disconnect()
      self.downloadCards[i]["edit"].clicked.disconnect()
      self.downloadCards[i]["delete"].clicked.disconnect()
      self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switch(_pos))
      self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switch(_pos)
      self.downloadCards[i]["up"].clicked.connect(lambda val, _pos = i: self.up(_pos))
      self.downloadCards[i]["down"].clicked.connect(lambda val, _pos = i: self.down(_pos))
      self.downloadCards[i]["edit"].clicked.connect(lambda val, _pos = i: self.edit(_pos))
      self.downloadCards[i]["delete"].clicked.connect(lambda val, _pos = i: self.delete(_pos))

  def edit(self, pos):
    name = self.downloadCards[pos]["name"].text()
    uid = self.downloadCards[pos]["uid"].text()
    type = self.downloadCards[pos]["type"].text()
    self.child = CreateDownload(self, name, uid, type, pos, "编辑下载对象")

  def delete(self, pos):
    item = self.downloadCards.pop(pos)
    # 如果保存失败，则回退操作并返回
    if self.save() == False:
      self.downloadCards.insert(pos, item)
      return
    item["download"].setParent(None)
    for i in range(len(self.downloadCards)):
      self.downloadCards[i]["combo"].clicked.disconnect()
      self.downloadCards[i]["up"].clicked.disconnect()
      self.downloadCards[i]["down"].clicked.disconnect()
      self.downloadCards[i]["edit"].clicked.disconnect()
      self.downloadCards[i]["delete"].clicked.disconnect()
      self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switch(_pos))
      self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switch(_pos)
      self.downloadCards[i]["up"].clicked.connect(lambda val, _pos = i: self.up(_pos))
      self.downloadCards[i]["down"].clicked.connect(lambda val, _pos = i: self.down(_pos))
      self.downloadCards[i]["edit"].clicked.connect(lambda val, _pos = i: self.edit(_pos))
      self.downloadCards[i]["delete"].clicked.connect(lambda val, _pos = i: self.delete(_pos))
    self.scroll_widget.adjustSize()
    self.stateChange()

  def add(self):
    self.child = CreateDownload(self)
    
  def deleteSelect(self):
    # 获取待删除列表
    deleteList = []
    for pos in range(len(self.downloadCards)):
      if self.downloadCards[pos]["select"]:
        deleteList.insert(0, pos)
    # 将所有元素弹出存储
    itemList = []
    for pos in deleteList:
      itemList.append(self.downloadCards.pop(pos))
    # 如果保存失败，则回退操作并返回
    if self.save() == False:
      for i in reversed(range(len(deleteList))):
        pos = deleteList[i]
        item = itemList[i]
        self.downloadCards.insert(pos, item)
      return
    # 删除每个item
    for item in itemList:
      item["download"].setParent(None)
    # 重新绑定功能
    for i in range(len(self.downloadCards)):
      self.downloadCards[i]["combo"].clicked.disconnect()
      self.downloadCards[i]["up"].clicked.disconnect()
      self.downloadCards[i]["down"].clicked.disconnect()
      self.downloadCards[i]["edit"].clicked.disconnect()
      self.downloadCards[i]["delete"].clicked.disconnect()
      self.downloadCards[i]["combo"].clicked.connect(lambda val, _pos = i: self.switch(_pos))
      self.downloadCards[i]["download"].mousePressEvent = lambda val, _pos = i: self.switch(_pos)
      self.downloadCards[i]["up"].clicked.connect(lambda val, _pos = i: self.up(_pos))
      self.downloadCards[i]["down"].clicked.connect(lambda val, _pos = i: self.down(_pos))
      self.downloadCards[i]["edit"].clicked.connect(lambda val, _pos = i: self.edit(_pos))
      self.downloadCards[i]["delete"].clicked.connect(lambda val, _pos = i: self.delete(_pos))
    # 调整scroll大小
    self.scroll_widget.adjustSize()
    # 更改按钮状态
    self.stateChange()

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
    # 备份
    backup = base_config["__main__"]["main"]["download_list"]
    try:
      base_config["__main__"]["main"]["download_list"] = downloadList
      saveJson(base_config, os.path.abspath("config.json"))
    except Exception as e:
      logger.error("下载配置保存失败")
      base_config["__main__"]["main"]["download_list"] = backup
      box = QMessageBox(self)
      box.setText(f"修改失败: {str(e)}")
      box.setWindowTitle(" Pixiv下载工具")
      box.setFont(Font.LEVEL3)
      okButton = box.addButton("好的", QMessageBox.ButtonRole.AcceptRole)
      okButton.setFont(Font.LEVEL4)
      box.setDefaultButton(okButton)
      box.setStyleSheet(
        """
        QLabel {
          color: red;
        }
        """
      )
      box.exec()
      return False
    else:
      logger.info("下载配置保存成功")
      return True


  def stateChange(self):
    for item in self.downloadCards:
      if item["select"]:
        self.state = self.State.SELECTED
        break
    else:
      self.state = self.State.NOT_SELECT


  def startAllDownload(self):
    downloadList = []
    for item in self.downloadCards:
      if item["select"]:
        downloadList.append({
          "uid": item["uid"].text(),
          "type": item["type"].text(),
          "name": item["name"].text()
        })
    self.download = SpiderDownload(self, downloadList)
    # 当程序退出时线程终止
    self.download.setDaemon(True)
    self.download.start()


  def stopDownload(self):
    """
    终止正在进行的测试线程
    """
    if self.download != None:
      self.state = self.State.STOPPING
      self.download.raise_exception()
      self.download = None

  
  def clearDownload(self):
    """
    删除所有下载记录
    """
    # 如果当前没有记录，那么直接返回
    if self.scroll_info_layout.count() == 0:
      return
    # 如果有记录，询问一下是否确认
    execute = False
    box = QMessageBox(self)
    box.setText("是否删除当前下载记录（不会删除实际下载文件）？")
    box.setWindowTitle(" Pixiv下载工具")
    box.setFont(Font.LEVEL3)
    yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
    noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
    yesButton.setFont(Font.LEVEL4)
    noButton.setFont(Font.LEVEL4)
    box.setDefaultButton(yesButton)
    yesButton.setShortcut("Y")
    noButton.setShortcut("N")
    box.setStyleSheet(
      """
      QLabel {
        color: rgb(0, 51, 153);
      }
      """
    )
    box.exec()
    if box.clickedButton() == yesButton:
      execute = True
    # 不执行
    if not execute:
      return
    for i in range(self.scroll_info_layout.count()):
      self.scroll_info_layout.itemAt(i).widget().deleteLater()
    # 记录信息从头开始
    self.count = 1
    self.downloadItemList = []
        

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return True


  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    return self.canSwitchOut()


class StateChangeEvent(QEvent):
  """
  下载状态变化，通知主线程进行操作
  """
  idType = QEvent.registerEventType()
  def __init__(self, state):
    super(StateChangeEvent, self).__init__(StateChangeEvent.idType)
    self.state = state


class AddContentEvent(QEvent):
  """
  新增下载内容显示，通知主线程进行操作
  """
  idType = QEvent.registerEventType()
  def __init__(self, content):
    super(AddContentEvent, self).__init__(AddContentEvent.idType)
    self.content = content


class SpiderDownload(threading.Thread):
  def __init__(self, target, downloadList):
    threading.Thread.__init__(self)
    self.target = target
    self.downloadList = downloadList
  

  def run(self):
    QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.DOWNLOADING))
    try:
      spider = Spider(self.addContent)
      for item in self.downloadList:
        name = item["name"]
        uid = item["uid"]
        type = item["type"]
        try:
          QtCore.QCoreApplication.postEvent(self.target, AddContentEvent({
            "type": "start",
            "name": name,
            "uid": uid,
            "route": type
          }))
          spider.download_by_info(uid, type)
        finally:
          QtCore.QCoreApplication.postEvent(self.target, AddContentEvent({
            "type": "end",
            "name": name,
            "uid": uid,
            "route": type
          }))
    except Exception as e:
      logger.error(e)
    finally:
      QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(None))
    

  def addContent(self, content):
    """
    ## 图片页面
    {
      "type": "gallery",
      "url": "abc",
      "title": "abc",
      "update": False
    }
    ## 图片
    {
      "type": "image",
      "url": "abc",
      # 可以没有path，表示尚未下载完成
      "path": "abc",
      "method": "abc"
      "update": False,
      # 可以没有，表示不特殊设置
      "color": "red"
    }
    ## 系列小说
    {
      "type": "series",
      "url": "abc",
      "title": "abc",
      "update": False
    }
    ## 小说
    {
      "type": "novel",
      "url": "abc",
      # 可以没有path，表示尚未下载完成
      "path": "abc",
      "method": "abc",
      "update": False,
      # 可以没有，表示不特殊设置
      "color": "red"
    }
    """
    QtCore.QCoreApplication.postEvent(self.target, AddContentEvent(content))


  def get_id(self):
    if hasattr(self, '_thread_id'):
      return self._thread_id
    for id, thread in threading._active.items():
      if thread is self:
        return id

  def raise_exception(self):
    thread_id = self.get_id() 
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
    if res > 1: 
      ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
      logger.error("SpiderDownload终止失败")