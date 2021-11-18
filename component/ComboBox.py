# 选择框

from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel


class QComboBox(QComboBox):
  # 禁用鼠标滚动更改值
  def wheelEvent(self, e):
    pass

class ComboBox(QFrame):

  def __init__(self, name, val, valList, inform, font, *args):
    super().__init__(*args)
    self.name = name
    self.val = val
    self.valList = valList
    self.inform = inform
    self.font = font
    self.initUI()

  def initUI(self):
    layout = QHBoxLayout()
    label = QLabel(self.name)
    label.setFont(self.font)
    layout.addWidget(label)
    self.combo = QComboBox()
    for item in self.valList:
      self.combo.addItem(item)
    self.combo.setCurrentText(self.val)
    self.combo.setFont(self.font)
    layout.addWidget(self.combo)
    layout.addStretch(1)

    # 设置最后的修改样式
    layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(layout)

    # 触发事件
    self.combo.currentTextChanged[str].connect(self.inform)
    
  # 设置新值
  def setValue(self, new_val):
    self.combo.setCurrentText(new_val)

  # 获取当前值
  def getValue(self):
    return self.combo.currentText()