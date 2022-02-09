# 开始下载

from PyQt6 import QtCore
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from .Font import Font
from . import logger


class StartDownload(QFrame):

  def __init__(self, name, uid, type, *args):
    super().__init__(*args)
    self.name = str(name)
    self.uid = str(uid)
    self.type = str(type)
    self.initUI()

  def initUI(self):
    startWidget = QLabel("下载开始")
    startWidget.setFont(Font.LEVEL2)
    startWidget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    startWidget.setFixedWidth(120)
    startWidget.setStyleSheet(
      """
      QLabel {
        border-radius: 2px;
        background-color: rgb(220, 220, 220);
        background-color: #d81e06;
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 2px;
        padding-top: 2px;
        color: white;
      }
      """
    )
    nameWidget = QLabel(self.name)
    nameWidget.setFont(Font.LEVEL3)
    uidWidget = QLabel("用户UID: {}".format(self.uid))
    uidWidget.setFont(Font.ENGLISH_LEVEL5)
    uidWidget.setStyleSheet(
      """
      color: rgb(60, 60, 60);
      """
    )
    typeWidget = QLabel("类型: {}".format(self.type))
    typeWidget.setFont(Font.ENGLISH_LEVEL5)
    typeWidget.setStyleSheet(
      """
      color: rgb(60, 60, 60);
      """
    )
    titleLine = QHBoxLayout()
    titleCol = QVBoxLayout()
    detailRow = QVBoxLayout()
    detailRow.addWidget(uidWidget)
    # detailRow.addSpacing(20)
    detailRow.addWidget(typeWidget)
    detailRow.addStretch(1)
    titleCol.addWidget(nameWidget)
    titleCol.addLayout(detailRow)
    titleLine.addWidget(startWidget)
    titleLine.addLayout(titleCol)

    self.setLayout(titleLine)
    self.setStyleSheet(
      """
      QFrame {
        background-color: rgb(238, 238, 238);
        background-color: #f59692;
      }
      """
    )
    