# True or False选项

from PyQt6 import QtCore
from PyQt6.QtWidgets import QCheckBox

class CheckBox(QCheckBox):

  def __init__(self, name, val, inform, font, *args):
    super().__init__(*args)
    self.name = name
    self.val = val
    self.inform = inform
    self.font = font
    self.initUI()

  def initUI(self):
    self.setText(self.name)
    self.setFont(self.font)
    if self.val:
      self.toggle()

    # 触发事件
    self.stateChanged.connect(lambda val : self.inform(True) if val == QtCore.Qt.CheckState.Checked.value else self.inform(False))
    
  # 设置为指定值
  def setValue(self, new_val):
    self.setCheckState(QtCore.Qt.CheckState.Checked if new_val else QtCore.Qt.CheckState.Unchecked)

  # 获取当前值
  def getValue(self):
    present = self.checkState()
    return True if present == QtCore.Qt.CheckState.Checked else False