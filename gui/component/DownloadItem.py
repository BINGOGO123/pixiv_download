# 下载项

import os
import webbrowser
from PyQt6 import QtCore
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from .Font import Font
from . import logger



class ImageDisplay(QLabel):
  def __init__(self, url, method, path, *args):
    super().__init__(*args)
    self.url = url
    self.method = method
    self.path = path
    self.initUI()
  def initUI(self):
    self.setWindowIcon(QIcon("icons/pixiv.svg"))
    self.setWindowTitle(" {}".format(self.url))
    pix = QPixmap(self.path)
    pix = pix.scaledToWidth(3000, QtCore.Qt.TransformationMode.SmoothTransformation)
    self.setPixmap(pix)
    self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    self.show()



class DownloadItem(QFrame):

  def __init__(self, order, title, url, imageList, *args):
    super().__init__(*args)
    self.order = str(order)
    self.title = str(title)
    self.url = str(url)
    self.imageList = imageList
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
    for image in self.imageList:
      try:
        imageUrl = str(image.get("url"))      
        imagePath = None if image.get("path") == None else str(image.get("path"))
        imageMethod = str(image.get("method"))
      except Exception as e:
        logger.error("DownloadItem image参数错误，image={}".format(image))
        continue
      self.addImage(imageUrl, imagePath, imageMethod)

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

  def openImage(self, imageUrl, imageMethod, imagePath):
    self.imageDisplay = ImageDisplay(imageUrl, imageMethod, imagePath)

  def addImage(self, imageUrl, imagePath, imageMethod):
    imageButton = QPushButton()
    if imagePath != None:
      imageButton.setIcon(QIcon(imagePath))
    else:
      imageButton.setIcon(QIcon("icons/image.svg"))
    imageButton.setIconSize(QtCore.QSize(50, 50))
    imageButton.setFixedWidth(50)
    imageButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 2px; 
      }
      """
    )
    urlLabel = QPushButton(imageUrl)
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
    urlLabel.clicked.connect(lambda : webbrowser.open_new(imageUrl))
    if imagePath == None:
      pathLabel = QPushButton("尚未下载完成")
    else:
      pathLabel = QPushButton(imagePath)
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
    if imagePath != None:
      pathLabel.clicked.connect(lambda : os.system(r'start "" "{}"'.format("\\".join(imagePath.split("\\")[:-1]))))
    methodLabel = QLabel(imageMethod)
    methodLabel.setFont(Font.LEVEL4)
    methodLabel.setStyleSheet(
      """
      background-color: transparent;
      """
    )
    infoWidget = QFrame()
    infoLine = QHBoxLayout()
    infoLine.addWidget(imageButton)
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
    infoLine.addSpacing(20)
    infoLine.addWidget(methodLabel)
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
    if imagePath != None:
      infoWidget.mousePressEvent = lambda x : None if os.system(r'start "" "{}"'.format(imagePath)) != None else None
      imageButton.clicked.connect(lambda x : os.system(r'start "" "{}"'.format(imagePath)))
    infoWidget.setToolTip("单击打开图片")
    self.infoRegion.addWidget(infoWidget)
    self.infoList.append({
      "imageButton": imageButton,
      "infoWidget": infoWidget,
      "url": urlLabel,
      "path": pathLabel,
      "method": methodLabel
    })

  def imageCount(self):
    """
    返回当前图片数量
    """
    return len(self.infoList)

  def changeImage(self, pos, imageUrl, imagePath, imageMethod):
    if(pos < 0 or pos >= len(self.infoList)):
      logger.error("DownloadItem.changeImage pos={}，超出范围[0, {}]".format(pos, len(self.infoList)))
      return
      
    info = self.infoList[pos]
    info["method"].setText(imageMethod)
    info["url"].setText(imageUrl)
    info["url"].disconnect()
    info["url"].clicked.connect(lambda : webbrowser.open_new(imageUrl))
    info["path"].disconnect()
    info["imageButton"].disconnect()
    info["infoWidget"].mousePressEvent = None
    if imagePath != None:
      info["imageButton"].setIcon(QIcon(imagePath))
      info["path"].setText(imagePath)
      info["infoWidget"].mousePressEvent = lambda x : None if os.system(r'start "" "{}"'.format(imagePath)) != None else None
      info["imageButton"].clicked.connect(lambda x : os.system(r'start "" "{}"'.format(imagePath)))
      info["path"].clicked.connect(lambda : os.system(r'start "" "{}"'.format("\\".join(imagePath.split("\\")[:-1]))))
    else:
      info["imageButton"].setIcon(QIcon("icons/image.svg"))
      info["path"].setText("尚未下载完成")
