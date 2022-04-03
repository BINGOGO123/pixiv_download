# 查看下载界面

from PyQt6.QtWidgets import QFrame, QHBoxLayout
from gui.ViewContent import ViewContent
from .ViewSide import ViewSide
from . import logger
from config import base_config

class View(QFrame):

  def __init__(self, addItem, *args):
    super().__init__(*args)
    self.addItem = addItem
    self.initUI()

  def initUI(self):
    # 内容部分，False表示不显示
    self.content = ViewContent(False)
    # 左侧边栏
    downloadDir = base_config["spider"]["save_dir_name"]
    downloadList = base_config["__main__"]["main"]["download_list"]
    self.side = ViewSide(downloadDir, downloadList, self.addItem, self.content.update)
    # 布局设置
    hbox = QHBoxLayout()
    hbox.addWidget(self.side)
    hbox.addWidget(self.content)
    hbox.setContentsMargins(0, 0, 0, 0);
    hbox.setSpacing(0)
    self.setLayout(hbox)
  
  def updateSide(self):
    """
    更新side
    """
    downloadDir = base_config["spider"]["save_dir_name"]
    downloadList = base_config["__main__"]["main"]["download_list"]
    self.side.update(downloadDir, downloadList)

  def addContent(self, newPath):
    """
    增加新内容，路径保持不变
    """
    self.content.add(newPath)

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return True
  
  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    return self.canSwitchOut()