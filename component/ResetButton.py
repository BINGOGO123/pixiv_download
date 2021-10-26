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
    self.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 4px; 
        border-radius: 8px;
        background-color: white;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    self.setFixedSize(26, 26)
    self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    self.setToolTip("撤销对该部分设置项的修改")
