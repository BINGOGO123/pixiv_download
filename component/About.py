# 关于界面

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class About(QFrame):

  def __init__(self, *args):
    super().__init__(*args)

    self.initUI()

  def initUI(self):
    level1 = QFont("宋体", 14, QFont.Weight.Bold)
    level2 = QFont("宋体", 12)
    level3 = QFont("宋体", 10)
    level4 = QFont("宋体", 10)

    layout = QVBoxLayout()
    title = QLabel("本软件仅供学习参考使用！")
    title.setFont(level1)
    author = QLabel("作者：Github@BINGOGO123")
    author.setFont(level4)
    email = QLabel("联系方式：416778940@qq.com")
    email.setFont(level4)
    layout.addWidget(title)
    layout.addWidget(author)
    layout.addWidget(email)
    layout.addStretch(1)
    self.setLayout(layout)

    self.setFrameShape(QFrame.Shape.StyledPanel)

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return True

  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    return self.canSwitchOut()
