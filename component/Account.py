# 账户界面

import sys
import PyQt6
from PyQt6 import QtCore
from PyQt6.QtCore import QFileSelector, QRegularExpression
from PyQt6.QtGui import QColor, QCursor, QFont, QIcon, QImage, QIntValidator, QPixmap, QRegularExpressionValidator, QTextCursor, QTextLine, QValidator
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget, QPushButton, QScrollArea, QScrollBar, QScroller, QVBoxLayout, QWidget, QPlainTextEdit

class Account(QFrame):

  def __init__(self, *args):
    super().__init__(*args)

    self.initUI()

  def initUI(self):
    layout = QVBoxLayout()
    title = QLabel("账户")
    layout.addWidget(title)
    layout.addStretch(1)
    self.setLayout(layout)

    self.setContentsMargins(8, 0, 0, 0)
    # self.setFrameShape(QFrame.Shape.StyledPanel)

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return True
    
  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    return self.canSwitchOut()

