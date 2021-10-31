# 重置按钮

from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

class ResetButton(QPushButton):

  def __init__(self, *args):
    super().__init__(*args)
    self.initUI()

  def initUI(self):
    self.setIcon(QIcon("icons/cancel.svg"))
    self.setIconSize(QtCore.QSize(12, 12))
    self.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 4px; 
        border-radius: 11px;
        background-color: white;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    self.setFixedSize(22, 22)
    # self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    self.setToolTip("撤销对该部分设置项的修改")
