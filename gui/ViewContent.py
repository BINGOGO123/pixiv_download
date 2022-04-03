# 查看下载界面内容栏

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from .component.Font import Font


class ViewContent(QFrame):

  def __init__(self, dir = False, *args):
    """
    dir = False 或 dir = None 表示不显示，否则显示dir文件夹内容
    """
    super().__init__(*args)
    self.dir = dir
    if dir == None:
      self.dir = False
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

  def update(self, newDir = None):
    """
    更新显示内容，None表示仅更新显示，False表示更新为不显示，否则更新显示新文件夹
    """
    print("update({})".format(newDir))
    if newDir != None:
      self.dir = newDir

  def add(self, newPath):
    """
    添加newPath
    """
    print("add({})".format(newPath))