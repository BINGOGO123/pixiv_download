# 选择文件夹

from PyQt6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton

class PathSelect(QFrame):

  def __init__(self, name, val, inform, font, *args):
    super().__init__(*args)
    self.name = name
    self.val = val
    self.inform = inform
    self.font = font
    self.initUI()

  def select(self):
    result = QFileDialog.getExistingDirectory(self, self.name)
    if result != "":
      self.setValue(result)

  def initUI(self):
    layout = QHBoxLayout()
    label = QLabel(self.name)
    label.setFont(self.font)
    layout.addWidget(label)

    self.valButton = QPushButton(self.val)
    self.valButton.setFont(self.font)
    self.valButton.setMinimumWidth(200)
    self.valButton.setStyleSheet(
      """
      QPushButton {
        background-color: rgb(245, 245, 245);
        border:none;
        padding:5px;
      }
      QPushButton:hover {
        background-color:rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    layout.addWidget(self.valButton)
    layout.addStretch(1)

    # 设置最后的修改样式
    layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(layout)

    # 触发事件
    self.valButton.clicked.connect(self.select)

  # 获取当前值
  def getValue(self):
    return self.valButton.text()
  
  # 设置新值
  def setValue(self, new_val):
    if new_val != self.valButton.text():
      self.valButton.setText(new_val)
      self.adjustSize()
      self.inform(new_val)
