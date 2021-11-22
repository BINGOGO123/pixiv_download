# 关于界面

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from .component.Font import Font


class About(QFrame):

  def __init__(self, *args):
    super().__init__(*args)

    self.initUI()

  def initUI(self):

    layout = QVBoxLayout()
    title = QLabel("本软件仅供学习参考使用！")
    title.setFont(Font.LEVEL1)
    author = QLabel("作者：Github@BINGOGO123")
    author.setFont(Font.LEVEL4)
    email = QLabel("联系方式：416778940@qq.com")
    email.setFont(Font.LEVEL4)
    layout.addWidget(title)
    layout.addWidget(author)
    layout.addWidget(email)
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
