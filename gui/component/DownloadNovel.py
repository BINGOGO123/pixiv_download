# 下载小说

import os
import webbrowser
from PyQt6 import QtCore
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from .Font import Font
from . import logger



class DownloadNovel(QFrame):

  def __init__(self, order, title, url, novelList, *args):
    super().__init__(*args)
    self.order = str(order)
    self.title = str(title)
    self.url = str(url)
    self.novelList = novelList
    self.initUI()

  def initUI(self):
    orderWidget = QLabel(self.order)
    orderWidget.setFont(Font.LEVEL4)
    orderWidget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    orderWidget.setStyleSheet(
      """
      QLabel {
        border-radius: 2px;
        background-color: rgb(220, 220, 220);
        background-color: rgb(210, 220, 238);
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 2px;
        padding-top: 2px;
      }
      """
    )
    titleWidget = QLabel(self.title)
    titleWidget.setFont(Font.LEVEL3)
    urlWidget = QLabel(self.url)
    urlWidget.setFont(Font.ENGLISH_LEVEL5)
    urlWidget.setOpenExternalLinks(True)
    urlWidget.setText("<a href='{}' style='color:rgb(120,120,120)'>{}</a>".format(self.url, self.url))
    urlWidget.setToolTip("打开网址")
    titleLine = QHBoxLayout()
    titleCol = QVBoxLayout()
    titleCol.addWidget(titleWidget)
    titleCol.addWidget(urlWidget)
    titleLine.addWidget(orderWidget)
    titleLine.addLayout(titleCol)
    titleLine.addStretch(1)

    self.infoRegion = QVBoxLayout()
    self.infoRegion.setSpacing(0)
    self.infoList = []
    for novel in self.novelList:
      try:
        novelUrl = str(novel.get("url"))      
        novelPath = None if novel.get("path") == None else str(novel.get("path"))
        novelMethod = str(novel.get("method"))
        novelColor = None if novel.get("color") == None else str(novel.get("color"))
      except Exception as e:
        logger.error("DownloadNovel novel参数错误，novel={}".format(novel))
        continue
      self.addNovel(novelUrl, novelPath, novelMethod, novelColor)

    finalLayout = QVBoxLayout()
    finalLayout.addLayout(titleLine)
    finalLayout.addLayout(self.infoRegion)
    # finalLayout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(finalLayout)
    self.setStyleSheet(
      """
      QFrame {
        background-color: rgb(238, 238, 238);
      }
      """
    )

  def addNovel(self, novelUrl, novelPath, novelMethod, novelColor = None):
    novelButton = QPushButton()
    if novelPath != None:
      novelButton.setIcon(QIcon("icons/novel.jpg"))
    else:
      novelButton.setIcon(QIcon("icons/novel_downloading.svg"))
    novelButton.setIconSize(QtCore.QSize(50, 50))
    novelButton.setFixedWidth(50)
    novelButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
      }
      """
    )
    urlLabel = QPushButton(novelUrl)
    urlLabel.setFont(Font.ENGLISH_LEVEL5)
    urlLabel.setStyleSheet(
      """
      QPushButton {
        background-color: transparent;
        text-decoration:underline;
        color: rgb(120, 120, 120);
        text-align: left;
      }
      """
    )
    urlLabel.setToolTip("打开网址")
    urlLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    urlLabel.clicked.connect(lambda : webbrowser.open_new(novelUrl))
    if novelPath == None:
      pathLabel = QPushButton("下载未完成")
    else:
      pathLabel = QPushButton(novelPath)
    pathLabel.setFont(Font.ENGLISH_LEVEL5)
    pathLabel.setStyleSheet(
      """
      QPushButton {
        background-color: transparent;
        text-decoration:underline;
        text-align: left;
      }
      """
    )
    pathLabel.setToolTip("打开文件所在位置")
    pathLabel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    if novelPath != None:
      pathLabel.clicked.connect(lambda : os.system(r'start "" "{}"'.format(os.path.dirname(novelPath))))
    methodLabel = QLabel(novelMethod)
    methodLabel.setFont(Font.LEVEL4)
    methodLabel.setFixedWidth(85)
    methodLabel.setFixedHeight(40)
    methodLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    if novelColor == "red":
      methodStyle = """
      background-color: #d81e06;
      color: white;
      border-radius: 2px;
      """
    elif novelColor == "blue":
      methodStyle = """
      background-color: #1296db;
      color: white;
      border-radius: 2px;
      """
    else:
      methodStyle = """
      background-color: rgb(175, 185, 203);
      border-radius: 2px;
      """
    methodLabel.setStyleSheet(methodStyle)
    infoWidget = QFrame()
    infoLine = QHBoxLayout()
    infoLine.addWidget(novelButton)
    infoLine.addWidget(methodLabel)
    infoRow1 = QHBoxLayout()
    infoRow1.addWidget(pathLabel)
    infoRow1.addStretch(1)
    infoRow2 = QHBoxLayout()
    infoRow2.addWidget(urlLabel)
    infoRow2.addStretch(1)
    infoCol = QVBoxLayout()
    infoCol.addStretch(1)
    infoCol.addLayout(infoRow1)
    infoCol.addStretch(1)
    infoCol.addLayout(infoRow2)
    infoCol.addStretch(1)
    infoLine.addLayout(infoCol)
    infoLine.addStretch(1)
    infoWidget.setLayout(infoLine)
    infoLine.setContentsMargins(4, 2, 20, 2)
    infoWidget.setContentsMargins(0, 0, 0, 0)
    infoWidget.setStyleSheet(
      """
      .QFrame {
        background-color: transparent;
        background-color: white;
        background-color: rgb(220, 220, 220);
      }
      .QFrame:hover {
        background-color: rgb(210, 220, 238);
        background-color: rgb(190, 200, 218);
      }
      """
    )
    if novelPath != None:
      infoWidget.mousePressEvent = lambda x : None if os.system(r'start "" "{}"'.format(novelPath)) != None else None
      novelButton.clicked.connect(lambda x : os.system(r'start "" "{}"'.format(novelPath)))
    infoWidget.setToolTip("单击打开小说")
    self.infoRegion.addWidget(infoWidget)
    self.infoList.append({
      "novelButton": novelButton,
      "infoWidget": infoWidget,
      "url": urlLabel,
      "path": pathLabel,
      "method": methodLabel
    })

  def novelCount(self):
    """
    返回当前小说数量
    """
    return len(self.infoList)

  def changeNovel(self, pos, novelUrl, novelPath, novelMethod, novelColor = None):
    if(pos < 0 or pos >= len(self.infoList)):
      logger.error("DownalodNovel.changeNovel pos={}，超出范围[0, {}]".format(pos, len(self.infoList)))
      return
      
    info = self.infoList[pos]
    info["method"].setText(novelMethod)
    if novelColor == "red":
      methodStyle = """
      background-color: #d81e06;
      color: white;
      border-radius: 2px;
      """
    elif novelColor == "blue":
      methodStyle = """
      background-color: #1296db;
      color: white;
      border-radius: 2px;
      """
    else:
      methodStyle = """
      background-color: rgb(175, 185, 203);
      border-radius: 2px;
      """
    info["method"].setStyleSheet(methodStyle)
    info["url"].setText(novelUrl)
    info["url"].disconnect()
    info["url"].clicked.connect(lambda : webbrowser.open_new(novelUrl))
    info["path"].disconnect()
    info["novelButton"].disconnect()
    info["infoWidget"].mousePressEvent = None
    if novelPath != None:
      info["novelButton"].setIcon(QIcon("icons/novel.jpg"))
      info["path"].setText(novelPath)
      info["infoWidget"].mousePressEvent = lambda x : None if os.system(r'start "" "{}"'.format(novelPath)) != None else None
      info["novelButton"].clicked.connect(lambda x : os.system(r'start "" "{}"'.format(novelPath)))
      info["path"].clicked.connect(lambda : os.system(r'start "" "{}"'.format(os.path.dirname(novelPath))))
    else:
      info["novelButton"].setIcon(QIcon("icons/novel_downloading.svg"))
      info["path"].setText("下载未完成")
